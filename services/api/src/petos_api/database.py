import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from petos_api.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url, echo=(settings.environment == "development")
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def check_postgres() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False


async def get_db():
    async with async_session() as session:
        yield session
