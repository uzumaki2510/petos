import hmac
import hashlib
from petos_api.redis_client import redis_client
from petos_api.core.config import settings
from petos_api.core.errors import AppError

# Lua script for atomic fixed-window rate limiting
# KEYS[1] = rate limit key
# ARGV[1] = max requests
# ARGV[2] = window seconds
LUA_RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[2])
end
if current > tonumber(ARGV[1]) then
    local ttl = redis.call("TTL", KEYS[1])
    return {-1, ttl}
end
return {current, redis.call("TTL", KEYS[1])}
"""


async def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """
    Atomic fixed-window rate limiter using Redis Lua script.
    """
    redis = redis_client
    if not redis:
        raise AppError(
            status_code=503, code="service_unavailable", message="Service Unavailable"
        )

    try:
        # returns [count, ttl] or [-1, ttl] if limit exceeded
        result = await redis.eval(
            LUA_RATE_LIMIT_SCRIPT, 1, key, max_requests, window_seconds
        )
        count, ttl = result
        if count == -1:
            raise AppError(
                status_code=429,
                code="too_many_requests",
                message="Too many requests. Please try again later.",
                headers={"Retry-After": str(ttl)},
            )
        return True
    except Exception as e:
        if isinstance(e, AppError):
            raise
        # If redis eval fails, we return 503 as instructed
        raise AppError(
            status_code=503, code="service_unavailable", message="Service Unavailable"
        )


def hash_identity_for_rate_limit(identity: str) -> str:
    """Hash the identity (e.g. email) using HMAC-SHA-256 for rate limit keys."""
    secret = settings.RATE_LIMIT_HMAC_SECRET.encode()
    return hmac.new(secret, identity.encode(), hashlib.sha256).hexdigest()


async def check_login_rate_limits(ip: str, identity: str) -> None:
    hashed_identity = hash_identity_for_rate_limit(identity)

    # Check IP
    await check_rate_limit(
        f"rl:login:ip:{ip}",
        settings.LOGIN_RATE_LIMIT_IP_MAX,
        settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
    )
    # Check Identity
    await check_rate_limit(
        f"rl:login:id:{hashed_identity}",
        settings.LOGIN_RATE_LIMIT_IDENTITY_MAX,
        settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
    )
    # Check Combined
    await check_rate_limit(
        f"rl:login:comb:{ip}:{hashed_identity}",
        settings.LOGIN_RATE_LIMIT_COMBINED_MAX,
        settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
    )


async def check_registration_rate_limits(ip: str, identity: str) -> None:
    hashed_identity = hash_identity_for_rate_limit(identity)

    # Check IP
    await check_rate_limit(
        f"rl:reg:ip:{ip}",
        settings.REGISTRATION_RATE_LIMIT_IP_MAX,
        settings.REGISTRATION_RATE_LIMIT_WINDOW_SECONDS,
    )
    # Check Identity
    await check_rate_limit(
        f"rl:reg:id:{hashed_identity}",
        settings.REGISTRATION_RATE_LIMIT_IDENTITY_MAX,
        settings.REGISTRATION_RATE_LIMIT_WINDOW_SECONDS,
    )
