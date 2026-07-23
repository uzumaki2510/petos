from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from petos_api.models.session import Session
import datetime


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_token_hash(self, token_hash: str) -> Optional[Session]:
        stmt = select(Session).where(Session.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, session: Session) -> None:
        self.session.add(session)

    async def update_last_seen(
        self,
        session_id: str,
        new_last_seen: datetime.datetime,
        new_expires_at: datetime.datetime,
    ) -> None:
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(last_seen_at=new_last_seen, expires_at=new_expires_at)
        )
        await self.session.execute(stmt)

    async def revoke_session(
        self, token_hash: str, revoked_at: datetime.datetime
    ) -> None:
        stmt = (
            update(Session)
            .where(Session.token_hash == token_hash)
            .values(revoked_at=revoked_at)
        )
        await self.session.execute(stmt)

    async def delete_expired_and_revoked(self, current_time: datetime.datetime) -> int:
        stmt = delete(Session).where(
            (Session.expires_at < current_time)
            | (Session.absolute_expires_at < current_time)
            | (Session.revoked_at.isnot(None))
        )
        result = await self.session.execute(stmt)
        return result.rowcount  # type: ignore
