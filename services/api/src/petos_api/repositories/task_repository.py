from typing import Optional, List, Tuple, Any
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from petos_api.models.task import Task
from petos_api.models.label import Label
from petos_api.models.task_label import TaskLabel


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: uuid.UUID) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_project(
        self, task_id: uuid.UUID, project_id: uuid.UUID
    ) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id, Task.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, task: Task) -> None:
        self.session.add(task)

    async def update_task_fields(
        self,
        task_id: uuid.UUID,
        expected_version: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        acceptance_criteria: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[uuid.UUID] = None,
        due_at: Optional[datetime] = None,
    ) -> bool:
        values = {
            "version": Task.version + 1,
            "updated_at": datetime.now(timezone.utc),
        }
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if acceptance_criteria is not None:
            values["acceptance_criteria"] = acceptance_criteria
        if priority is not None:
            values["priority"] = priority
        if assigned_to is not None:
            values["assigned_to"] = assigned_to
        if due_at is not None:
            values["due_at"] = due_at

        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.version == expected_version)
            .values(**values)
        )
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def update_status(
        self,
        task_id: uuid.UUID,
        expected_version: int,
        target_status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        clear_completed_at: bool = False,
    ) -> bool:
        values = {
            "status": target_status,
            "version": Task.version + 1,
            "updated_at": datetime.now(timezone.utc),
        }
        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        elif clear_completed_at:
            values["completed_at"] = None

        stmt = (
            update(Task)
            .where(Task.id == task_id, Task.version == expected_version)
            .values(**values)
        )
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def archive_task(self, task_id: uuid.UUID, expected_version: int) -> bool:
        now = datetime.now(timezone.utc)
        stmt = (
            update(Task)
            .where(
                Task.id == task_id,
                Task.version == expected_version,
                Task.archived_at.is_(None),
            )
            .values(archived_at=now, version=Task.version + 1, updated_at=now)
        )
        result = await self.session.execute(stmt)
        return getattr(result, "rowcount", 0) > 0

    async def get_labels_for_task(self, task_id: uuid.UUID) -> List[Label]:
        stmt = (
            select(Label)
            .join(TaskLabel, Label.id == TaskLabel.label_id)
            .where(TaskLabel.task_id == task_id)
            .order_by(Label.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_task_labels(
        self, task_id: uuid.UUID, label_ids: List[uuid.UUID]
    ) -> None:
        # Clear existing
        from sqlalchemy import delete

        await self.session.execute(
            delete(TaskLabel).where(TaskLabel.task_id == task_id)
        )
        for lid in label_ids:
            self.session.add(TaskLabel(task_id=task_id, label_id=lid))

    async def query_tasks(
        self,
        project_id: uuid.UUID,
        statuses: Optional[List[str]] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[uuid.UUID] = None,
        label_id_or_slug: Optional[str] = None,
        search_query: Optional[str] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        include_archived: bool = False,
        sort_by: str = "-created_at",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Task], int]:
        conditions = [Task.project_id == project_id]

        if not include_archived:
            conditions.append(Task.archived_at.is_(None))

        if statuses:
            conditions.append(Task.status.in_(statuses))

        if priority:
            conditions.append(Task.priority == priority)

        if assigned_to:
            conditions.append(Task.assigned_to == assigned_to)

        if due_before:
            conditions.append(Task.due_at <= due_before)

        if due_after:
            conditions.append(Task.due_at >= due_after)

        if search_query:
            escaped = (
                search_query.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            term = f"%{escaped}%"
            conditions.append(or_(Task.title.ilike(term), Task.description.ilike(term)))

        if label_id_or_slug:
            # Check if UUID or slug
            try:
                lid = uuid.UUID(label_id_or_slug)
                conditions.append(
                    Task.id.in_(
                        select(TaskLabel.task_id).where(TaskLabel.label_id == lid)
                    )
                )
            except ValueError:
                conditions.append(
                    Task.id.in_(
                        select(TaskLabel.task_id)
                        .join(Label, Label.id == TaskLabel.label_id)
                        .where(
                            Label.project_id == project_id,
                            func.lower(Label.slug) == label_id_or_slug.lower(),
                        )
                    )
                )

        count_stmt = select(func.count(Task.id)).where(and_(*conditions))
        total = await self.session.scalar(count_stmt) or 0

        # Sorting
        sort_map: dict[str, Any] = {
            "created_at": Task.created_at.asc(),
            "-created_at": Task.created_at.desc(),
            "updated_at": Task.updated_at.asc(),
            "-updated_at": Task.updated_at.desc(),
            "due_at": Task.due_at.asc(),
            "-due_at": Task.due_at.desc(),
            "priority": Task.priority.asc(),
            "task_number": Task.task_number.asc(),
            "-task_number": Task.task_number.desc(),
        }
        sort_column = sort_map.get(sort_by, Task.created_at.desc())

        stmt = (
            select(Task)
            .where(and_(*conditions))
            .order_by(sort_column)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total
