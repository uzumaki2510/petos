from typing import Optional, List, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from petos_api.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, project_id: uuid.UUID) -> Optional[Project]:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(
        self, organization_id: uuid.UUID, slug: str
    ) -> Optional[Project]:
        stmt = select(Project).where(
            Project.organization_id == organization_id, Project.slug == slug
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_key(
        self, organization_id: uuid.UUID, key: str
    ) -> Optional[Project]:
        stmt = select(Project).where(
            Project.organization_id == organization_id, Project.key == key
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def allocate_next_task_number(self, project_id: uuid.UUID) -> int:
        stmt = (
            update(Project)
            .where(Project.id == project_id)
            .values(next_task_number=Project.next_task_number + 1)
            .returning(Project.next_task_number - 1)
        )
        result = await self.session.execute(stmt)
        val = result.scalar_one_or_none()
        if val is None:
            raise ValueError(f"Project {project_id} not found")
        return val

    async def get_projects_for_organization(
        self, organization_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[Project], int]:
        count_stmt = select(func.count(Project.id)).where(
            Project.organization_id == organization_id
        )
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    def add(self, project: Project) -> None:
        self.session.add(project)

    async def update(
        self, project_id: uuid.UUID, name: str, description: Optional[str]
    ) -> None:
        stmt = (
            update(Project)
            .where(Project.id == project_id)
            .values(name=name, description=description)
        )
        await self.session.execute(stmt)

    async def archive(self, project_id: uuid.UUID) -> None:
        stmt = update(Project).where(Project.id == project_id).values(status="archived")
        await self.session.execute(stmt)
