import asyncio
import logging
from petos_api.database import async_session
from petos_api.repositories.session_repository import SessionRepository
from petos_api.models.base import utc_now

logger = logging.getLogger(__name__)


async def cleanup_expired_sessions():
    async with async_session() as session:
        repo = SessionRepository(session)
        now = utc_now()
        deleted_count = await repo.delete_expired_and_revoked(now)
        await session.commit()
        logger.info(f"Cleaned up {deleted_count} expired/revoked sessions.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(cleanup_expired_sessions())
