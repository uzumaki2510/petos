from typing import Optional, List, Tuple
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from petos_api.models.task_comment import TaskComment


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, comment_id: uuid.UUID) -> Optional[TaskComment]:
        stmt = select(TaskComment).where(TaskComment.id == comment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, comment: TaskComment) -> None:
        self.session.add(comment)

    async def update_comment(
        self, comment_id: uuid.UUID, expected_version: int, body: str
    ) -> bool:
        stmt = (
            update(TaskComment)
            .where(
                TaskComment.id == comment_id, TaskComment.version == expected_version
            )
            .values(
                body=body,
                version=TaskComment.version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_comments_for_task(
        self, task_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[TaskComment], int]:
        count_stmt = select(func.count(TaskComment.id)).where(
            TaskComment.task_id == task_id
        )
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(TaskComment)
            .where(TaskComment.task_id == task_id)
            .order_by(TaskComment.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total
