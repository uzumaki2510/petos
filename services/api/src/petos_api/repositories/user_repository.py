from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from petos_api.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_normalized_email(self, normalized_email: str) -> Optional[User]:
        stmt = select(User).where(User.normalized_email == normalized_email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, user: User) -> None:
        self.session.add(user)
