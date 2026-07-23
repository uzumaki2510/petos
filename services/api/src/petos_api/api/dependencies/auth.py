from typing import Annotated
import datetime
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.models.user import User
from petos_api.repositories.user_repository import UserRepository
from petos_api.repositories.session_repository import SessionRepository
from petos_api.core.security import hash_session_token
from petos_api.core.config import settings
from petos_api.core.errors import AppError
from petos_api.models.base import utc_now


def get_session_token(request: Request) -> str:
    token = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise AppError(
            status_code=401, code="unauthenticated", message="Missing session cookie"
        )
    return token


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(get_session_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    hashed_token = hash_session_token(token)
    session_repo = SessionRepository(db)
    user_repo = UserRepository(db)

    session = await session_repo.get_by_token_hash(hashed_token)
    if not session:
        raise AppError(
            status_code=401, code="unauthenticated", message="Invalid session"
        )

    now = utc_now()
    if session.revoked_at is not None:
        raise AppError(
            status_code=401, code="unauthenticated", message="Session revoked"
        )

    if session.expires_at < now or session.absolute_expires_at < now:
        raise AppError(
            status_code=401, code="unauthenticated", message="Session expired"
        )

    user = await user_repo.get_by_id(session.user_id)
    if not user or user.status == "disabled":
        raise AppError(
            status_code=401, code="unauthenticated", message="User account disabled"
        )

    # Throttled last_seen_at update
    time_since_last_seen = (now - session.last_seen_at).total_seconds()
    if time_since_last_seen > settings.SESSION_LAST_SEEN_UPDATE_INTERVAL_SECONDS:
        # Extend idle, but cap at absolute
        new_idle = min(
            now + datetime.timedelta(seconds=settings.SESSION_IDLE_TTL_SECONDS),
            session.absolute_expires_at,
        )
        await session_repo.update_last_seen(str(session.id), now, new_idle)
        await db.commit()

    return user
