from typing import Optional, List, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from petos_api.models.organization_membership import OrganizationMembership
from petos_api.models.organization import Organization


class MembershipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_membership(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[OrganizationMembership]:
        stmt = select(OrganizationMembership).where(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_organizations_for_user(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[Organization], int]:
        from sqlalchemy import func

        # Total count
        count_stmt = select(func.count(OrganizationMembership.id)).where(
            OrganizationMembership.user_id == user_id
        )
        total = await self.session.scalar(count_stmt) or 0

        # Paginated items
        stmt = (
            select(Organization)
            .join(
                OrganizationMembership,
                Organization.id == OrganizationMembership.organization_id,
            )
            .where(OrganizationMembership.user_id == user_id)
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    def add(self, membership: OrganizationMembership) -> None:
        self.session.add(membership)
