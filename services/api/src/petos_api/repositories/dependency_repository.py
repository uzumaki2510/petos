from typing import Optional, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from petos_api.models.task_dependency import TaskDependency
from petos_api.models.task import Task


class DependencyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def acquire_project_advisory_lock(self, project_id: uuid.UUID) -> None:
        """Acquire a transaction-level advisory lock for the given project_id."""
        stmt = text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))")
        lock_key = f"project_dep_lock:{project_id}"
        await self.session.execute(stmt, {"lock_key": lock_key})

    async def get_by_pair(
        self, task_id: uuid.UUID, depends_on_task_id: uuid.UUID
    ) -> Optional[TaskDependency]:
        stmt = select(TaskDependency).where(
            TaskDependency.task_id == task_id,
            TaskDependency.depends_on_task_id == depends_on_task_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, dependency_id: uuid.UUID) -> Optional[TaskDependency]:
        stmt = select(TaskDependency).where(TaskDependency.id == dependency_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, dependency: TaskDependency) -> None:
        self.session.add(dependency)

    async def delete(self, dependency_id: uuid.UUID) -> bool:
        stmt = delete(TaskDependency).where(TaskDependency.id == dependency_id)
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_dependencies_for_task(
        self, task_id: uuid.UUID
    ) -> List[TaskDependency]:
        stmt = (
            select(TaskDependency)
            .where(TaskDependency.task_id == task_id)
            .order_by(TaskDependency.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_project_dependencies(
        self, project_id: uuid.UUID
    ) -> List[TaskDependency]:
        """Fetch all dependency pairs in the project for graph traversal."""
        stmt = (
            select(TaskDependency)
            .join(Task, Task.id == TaskDependency.task_id)
            .where(Task.project_id == project_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_unresolved_dependencies_for_task(
        self, task_id: uuid.UUID
    ) -> List[Task]:
        """Returns prerequisite tasks that are NOT completed or cancelled."""
        stmt = (
            select(Task)
            .join(TaskDependency, Task.id == TaskDependency.depends_on_task_id)
            .where(
                TaskDependency.task_id == task_id,
                Task.status.notin_(["completed", "cancelled"]),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
