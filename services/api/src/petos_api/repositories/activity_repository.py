from typing import List, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from petos_api.models.task_activity import TaskActivity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, activity: TaskActivity) -> None:
        self.session.add(activity)

    async def get_activities_for_task(
        self, task_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[TaskActivity], int]:
        count_stmt = select(func.count(TaskActivity.id)).where(
            TaskActivity.task_id == task_id
        )
        total = await self.session.scalar(count_stmt) or 0

        # Stable ordering: created_at ascending, then id ascending
        stmt = (
            select(TaskActivity)
            .where(TaskActivity.task_id == task_id)
            .order_by(TaskActivity.created_at.asc(), TaskActivity.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total
