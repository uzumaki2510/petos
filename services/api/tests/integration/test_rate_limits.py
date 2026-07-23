"""
Rate-limit integration tests.

These tests require a running Redis instance (uses REDIS_URL env var, defaults
to the dev Redis at localhost:6379).  Each test uses a unique prefix so tests
do not interfere with each other or with production keys.

Skip these tests with: pytest -m "not rate_limit" when Redis is unavailable.
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from redis.asyncio import Redis
from petos_api.core.config import settings
from petos_api.core.errors import AppError
from petos_api.core.rate_limit import (
    LUA_RATE_LIMIT_SCRIPT,
    hash_identity_for_rate_limit,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def redis():
    """Real Redis connection — skipped if unavailable."""
    client = Redis.from_url(settings.redis_url, decode_responses=False)
    try:
        await client.ping()
    except Exception as e:
        pytest.skip(f"Redis unavailable: {e}")
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def rl_prefix(redis):
    """Returns a unique test-run prefix and cleans up all keys after the test."""
    prefix = f"test:rl:{uuid4().hex[:8]}"
    yield prefix
    # Cleanup: delete all keys with this prefix
    keys = await redis.keys(f"{prefix}:*")
    if keys:
        await redis.delete(*keys)


async def _check_limit(redis: Redis, key: str, max_requests: int, window: int):
    """Run the Lua rate-limit script directly against a real Redis."""
    result = await redis.eval(LUA_RATE_LIMIT_SCRIPT, 1, key, max_requests, window)
    count, ttl = result
    if count == -1:
        raise AppError(
            status_code=429,
            code="too_many_requests",
            message="Too many requests",
            headers={"Retry-After": str(ttl)},
        )
    return int(count)


# ── Lua script atomicity ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_lua_script_atomicity(redis, rl_prefix):
    """Each call increments exactly once — confirms INCR+EXPIRE atomicity."""
    key = f"{rl_prefix}:atomicity"
    for i in range(5):
        count = await _check_limit(redis, key, 10, 900)
        assert count == i + 1, f"Expected {i + 1}, got {count}"


# ── IP limit ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_ip_limit(redis, rl_prefix):
    """After IP_MAX requests, the next request raises 429 with Retry-After."""
    ip = "10.0.0.1"
    key = f"{rl_prefix}:login:ip:{ip}"
    max_req = 5  # low value for test speed
    window = 900

    for _ in range(max_req):
        await _check_limit(redis, key, max_req, window)

    with pytest.raises(AppError) as exc:
        await _check_limit(redis, key, max_req, window)
    assert exc.value.status_code == 429
    assert "Retry-After" in exc.value.headers
    assert int(exc.value.headers["Retry-After"]) > 0


# ── Identity limit ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_identity_limit(redis, rl_prefix):
    """Identity bucket enforces per-user limits independently of IP."""
    identity = hash_identity_for_rate_limit("targeted@example.com")
    key = f"{rl_prefix}:login:id:{identity}"
    max_req = 3
    window = 900

    for _ in range(max_req):
        await _check_limit(redis, key, max_req, window)

    with pytest.raises(AppError) as exc:
        await _check_limit(redis, key, max_req, window)
    assert exc.value.status_code == 429


# ── Combined limit ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_combined_limit(redis, rl_prefix):
    """Combined IP+identity bucket is enforced separately from both."""
    ip = "10.0.0.2"
    identity = hash_identity_for_rate_limit("combined@example.com")
    key = f"{rl_prefix}:login:comb:{ip}:{identity}"
    max_req = 3
    window = 900

    for _ in range(max_req):
        await _check_limit(redis, key, max_req, window)

    with pytest.raises(AppError) as exc:
        await _check_limit(redis, key, max_req, window)
    assert exc.value.status_code == 429


# ── Registration IP limit ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registration_ip_limit(redis, rl_prefix):
    """Registration uses the 3600-second window, not the login 900-second window."""
    ip = "10.0.0.3"
    key = f"{rl_prefix}:reg:ip:{ip}"
    max_req = 4
    registration_window = 3600  # must be 3600, not 900

    for _ in range(max_req):
        await _check_limit(redis, key, max_req, registration_window)

    with pytest.raises(AppError) as exc:
        await _check_limit(redis, key, max_req, registration_window)
    assert exc.value.status_code == 429

    # Verify TTL is consistent with registration window
    ttl = await redis.ttl(key)
    assert ttl > 0
    # TTL should be closer to 3600 than to 900 (was set from first request)
    assert ttl > 900, f"Expected TTL > 900 (registration window), got {ttl}"


# ── Registration identity limit ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registration_identity_limit(redis, rl_prefix):
    """Registration identity limit uses a 3600-second window."""
    identity = hash_identity_for_rate_limit("reg-targeted@example.com")
    key = f"{rl_prefix}:reg:id:{identity}"
    max_req = 2
    window = 3600

    for _ in range(max_req):
        await _check_limit(redis, key, max_req, window)

    with pytest.raises(AppError) as exc:
        await _check_limit(redis, key, max_req, window)
    assert exc.value.status_code == 429
    ttl = await redis.ttl(key)
    assert ttl > 900, f"Expected TTL > 900 (3600s window), got {ttl}"


# ── HMAC identity hashing ─────────────────────────────────────────────────────


def test_hmac_identity_does_not_expose_email():
    """The rate-limit identity key must not contain the raw email address."""
    email = "sensitive@example.com"
    hashed = hash_identity_for_rate_limit(email)

    assert email not in hashed, "Raw email must not appear in identity hash"
    assert "@" not in hashed, "Email characters must not appear in identity hash"
    assert len(hashed) == 64, "HMAC-SHA256 hex digest must be 64 chars"

    # Different emails must produce different hashes
    hashed2 = hash_identity_for_rate_limit("other@example.com")
    assert hashed != hashed2


def test_hmac_identity_is_deterministic():
    """Same email must always produce the same hash (needed for rate limit keys)."""
    email = "stable@example.com"
    h1 = hash_identity_for_rate_limit(email)
    h2 = hash_identity_for_rate_limit(email)
    assert h1 == h2


# ── Retry-After header ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retry_after_header_is_positive(redis, rl_prefix):
    """429 response must include a positive Retry-After value."""
    key = f"{rl_prefix}:retry:ip:1.2.3.4"
    await _check_limit(redis, key, 1, 60)

    with pytest.raises(AppError) as exc:
        await _check_limit(redis, key, 1, 60)

    error = exc.value
    assert error.status_code == 429
    assert "Retry-After" in error.headers
    ttl = int(error.headers["Retry-After"])
    assert ttl > 0, "Retry-After must be a positive number of seconds"


# ── Redis unavailable → 503 ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_redis_unavailable_returns_503():
    """If Redis is unreachable, check_rate_limit must return 503."""
    from unittest.mock import patch, AsyncMock
    from petos_api.core import rate_limit as rl_module

    # Patch the global redis_client with one that raises on eval
    bad_redis = AsyncMock()
    bad_redis.eval.side_effect = ConnectionError("Redis down")

    with patch.object(rl_module, "redis_client", bad_redis):
        with pytest.raises(AppError) as exc:
            await rl_module.check_rate_limit("any:key", 10, 60)
    assert exc.value.status_code == 503


# ── Window value correctness ──────────────────────────────────────────────────


def test_config_rate_limit_windows_are_correct():
    """
    Confirm settings have the exact approved values.
    Login: 900s window.
    Registration: 3600s window.
    """
    assert settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS == 900, (
        f"Login window must be 900s, got {settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS}"
    )
    assert settings.REGISTRATION_RATE_LIMIT_WINDOW_SECONDS == 3600, (
        f"Reg window must be 3600s, got {settings.REGISTRATION_RATE_LIMIT_WINDOW_SECONDS}"
    )
    assert settings.LOGIN_RATE_LIMIT_IP_MAX == 20
    assert settings.LOGIN_RATE_LIMIT_IDENTITY_MAX == 5
    assert settings.LOGIN_RATE_LIMIT_COMBINED_MAX == 5
    assert settings.REGISTRATION_RATE_LIMIT_IP_MAX == 10
    assert settings.REGISTRATION_RATE_LIMIT_IDENTITY_MAX == 3
