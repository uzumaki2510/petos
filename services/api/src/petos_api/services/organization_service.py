from typing import Tuple, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.models.organization_membership import OrganizationMembership
from petos_api.repositories.organization_repository import OrganizationRepository
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from petos_api.core.errors import AppError


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.db_session = session
        self.org_repo = OrganizationRepository(session)
        self.membership_repo = MembershipRepository(session)

    async def _require_membership(
        self,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        required_roles: Optional[List[str]] = None,
    ) -> OrganizationMembership:
        membership = await self.membership_repo.get_membership(user_id, org_id)
        if not membership:
            # Cross-tenant 404 behaviour
            raise AppError(
                status_code=404, code="not_found", message="Organization not found"
            )

        if required_roles and membership.role not in required_roles:
            raise AppError(
                status_code=403, code="forbidden", message="Insufficient permissions"
            )

        return membership

    async def get_user_organizations(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[OrganizationResponse], int]:
        items, total = await self.membership_repo.get_organizations_for_user(
            user_id, limit, offset
        )

        responses = [
            OrganizationResponse(
                id=org.id,
                name=org.name,
                slug=org.slug,
                created_at=org.created_at,
                updated_at=org.updated_at,
            )
            for org in items
        ]
        return responses, total

    async def get_organization(
        self, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> OrganizationResponse:
        await self._require_membership(user_id, org_id)
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise AppError(
                status_code=404, code="not_found", message="Organization not found"
            )

        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            created_at=org.created_at,
            updated_at=org.updated_at,
        )

    async def update_organization(
        self, user_id: uuid.UUID, org_id: uuid.UUID, req: OrganizationUpdateRequest
    ) -> OrganizationResponse:
        await self._require_membership(
            user_id, org_id, required_roles=["owner", "admin"]
        )

        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise AppError(
                status_code=404, code="not_found", message="Organization not found"
            )

        await self.org_repo.update(org_id, req.name)
        await self.db_session.commit()
        await self.db_session.refresh(org)

        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            created_at=org.created_at,
            updated_at=org.updated_at,
        )
