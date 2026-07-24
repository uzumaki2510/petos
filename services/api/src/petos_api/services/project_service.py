from typing import Tuple, List, Optional
import uuid
import re
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.models.project import Project
from petos_api.repositories.project_repository import ProjectRepository
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.schemas.project import (
    ProjectResponse,
    ProjectCreateRequest,
    ProjectUpdateRequest,
)
from petos_api.core.errors import AppError


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.db_session = session
        self.project_repo = ProjectRepository(session)
        self.membership_repo = MembershipRepository(session)

    async def _require_membership(
        self,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        required_roles: Optional[List[str]] = None,
    ) -> None:
        membership = await self.membership_repo.get_membership(user_id, org_id)
        if not membership:
            raise AppError(
                status_code=404, code="not_found", message="Organization not found"
            )

        if required_roles and membership.role not in required_roles:
            raise AppError(
                status_code=403, code="forbidden", message="Insufficient permissions"
            )

    def _generate_slug(self, name: str) -> str:
        base_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if not base_slug:
            base_slug = "project"
        return f"{base_slug}-{uuid.uuid4().hex[:6]}"

    async def _generate_default_key(self, org_id: uuid.UUID, name: str) -> str:
        cleaned = re.sub(r"[^A-Z0-9]", "", name.upper())
        if not cleaned or not cleaned[0].isalpha():
            cleaned = "PET" + cleaned
        base_key = cleaned[:10]
        if len(base_key) < 2:
            base_key = base_key + "X"

        candidate = base_key
        counter = 1
        while await self.project_repo.get_by_key(org_id, candidate):
            suffix = str(counter)
            max_base = 10 - len(suffix)
            candidate = base_key[:max_base] + suffix
            counter += 1
        return candidate

    async def get_projects(
        self, user_id: uuid.UUID, org_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[ProjectResponse], int]:
        await self._require_membership(user_id, org_id)
        items, total = await self.project_repo.get_projects_for_organization(
            org_id, limit, offset
        )

        responses = [
            ProjectResponse(
                id=p.id,
                organization_id=p.organization_id,
                name=p.name,
                slug=p.slug,
                key=p.key,
                description=p.description,
                status=p.status,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in items
        ]
        return responses, total

    async def get_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> ProjectResponse:
        p = await self.project_repo.get_by_id(project_id)
        if not p:
            raise AppError(
                status_code=404, code="not_found", message="Project not found"
            )

        await self._require_membership(user_id, p.organization_id)

        return ProjectResponse(
            id=p.id,
            organization_id=p.organization_id,
            name=p.name,
            slug=p.slug,
            key=p.key,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    async def create_project(
        self, user_id: uuid.UUID, org_id: uuid.UUID, req: ProjectCreateRequest
    ) -> ProjectResponse:
        await self._require_membership(
            user_id, org_id, required_roles=["owner", "admin", "member"]
        )

        if req.key:
            key_val = req.key.upper()
            if not re.match(r"^[A-Z][A-Z0-9]{1,9}$", key_val):
                raise AppError(
                    status_code=422,
                    code="unprocessable_entity",
                    message="Project key must be 2-10 uppercase alphanumeric characters starting with a letter",
                )
            existing = await self.project_repo.get_by_key(org_id, key_val)
            if existing:
                raise AppError(
                    status_code=409,
                    code="duplicate_key",
                    message=f"Project key '{key_val}' already exists in this organization",
                )
        else:
            key_val = await self._generate_default_key(org_id, req.name)

        p = Project(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=req.name,
            slug=self._generate_slug(req.name),
            key=key_val,
            next_task_number=1,
            description=req.description,
            status="active",
            created_by=user_id,
        )
        self.project_repo.add(p)
        await self.db_session.commit()
        await self.db_session.refresh(p)

        return ProjectResponse(
            id=p.id,
            organization_id=p.organization_id,
            name=p.name,
            slug=p.slug,
            key=p.key,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    async def update_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID, req: ProjectUpdateRequest
    ) -> ProjectResponse:
        p = await self.project_repo.get_by_id(project_id)
        if not p:
            raise AppError(
                status_code=404, code="not_found", message="Project not found"
            )

        await self._require_membership(
            user_id, p.organization_id, required_roles=["owner", "admin", "member"]
        )

        if p.status == "archived":
            raise AppError(
                status_code=400,
                code="invalid_state",
                message="Archived projects cannot be updated",
            )

        await self.project_repo.update(project_id, req.name, req.description)
        await self.db_session.commit()
        await self.db_session.refresh(p)

        return ProjectResponse(
            id=p.id,
            organization_id=p.organization_id,
            name=p.name,
            slug=p.slug,
            key=p.key,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    async def archive_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> ProjectResponse:
        p = await self.project_repo.get_by_id(project_id)
        if not p:
            raise AppError(
                status_code=404, code="not_found", message="Project not found"
            )

        await self._require_membership(
            user_id, p.organization_id, required_roles=["owner", "admin"]
        )

        if p.status != "archived":
            await self.project_repo.archive(project_id)
            await self.db_session.commit()
            await self.db_session.refresh(p)

        return ProjectResponse(
            id=p.id,
            organization_id=p.organization_id,
            name=p.name,
            slug=p.slug,
            key=p.key,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
