from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from petos_api.models.organization import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, organization_id: uuid.UUID) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.id == organization_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, organization: Organization) -> None:
        self.session.add(organization)

    async def update(self, organization_id: uuid.UUID, name: str) -> None:
        stmt = (
            update(Organization)
            .where(Organization.id == organization_id)
            .values(name=name)
        )
        await self.session.execute(stmt)
