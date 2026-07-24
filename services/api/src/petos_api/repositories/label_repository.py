from typing import Optional, List, Tuple
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from petos_api.models.label import Label


class LabelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, label_id: uuid.UUID) -> Optional[Label]:
        stmt = select(Label).where(Label.id == label_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, project_id: uuid.UUID, slug: str) -> Optional[Label]:
        stmt = select(Label).where(
            Label.project_id == project_id, func.lower(Label.slug) == slug.lower()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, project_id: uuid.UUID, name: str) -> Optional[Label]:
        stmt = select(Label).where(
            Label.project_id == project_id, func.lower(Label.name) == name.lower()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, label: Label) -> None:
        self.session.add(label)

    async def update_label(
        self,
        label_id: uuid.UUID,
        expected_version: int,
        name: str,
        slug: str,
        color: str,
    ) -> bool:
        stmt = (
            update(Label)
            .where(Label.id == label_id, Label.version == expected_version)
            .values(
                name=name,
                slug=slug,
                color=color,
                version=Label.version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_labels_for_project(
        self, project_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Label], int]:
        count_stmt = select(func.count(Label.id)).where(Label.project_id == project_id)
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Label)
            .where(Label.project_id == project_id)
            .order_by(Label.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total
