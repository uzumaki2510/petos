import logging
from redis.asyncio import Redis
from petos_api.core.config import settings

logger = logging.getLogger(__name__)

redis_client = Redis.from_url(settings.redis_url)


async def check_redis() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False
