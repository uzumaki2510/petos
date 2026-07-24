from typing import Tuple, List, Optional, Dict, Set
import uuid
import re
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.models.task import Task
from petos_api.models.task_comment import TaskComment
from petos_api.models.label import Label
from petos_api.models.task_dependency import TaskDependency
from petos_api.models.task_activity import TaskActivity
from petos_api.models.project import Project

from petos_api.repositories.task_repository import TaskRepository
from petos_api.repositories.comment_repository import CommentRepository
from petos_api.repositories.label_repository import LabelRepository
from petos_api.repositories.dependency_repository import DependencyRepository
from petos_api.repositories.activity_repository import ActivityRepository
from petos_api.repositories.project_repository import ProjectRepository
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.repositories.user_repository import UserRepository

from petos_api.schemas.task import (
    TaskResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskTransitionRequest,
    TaskArchiveRequest,
    BoardViewResponse,
    BoardColumnResponse,
)
from petos_api.schemas.comment import (
    CommentResponse,
    CommentCreateRequest,
    CommentUpdateRequest,
)
from petos_api.schemas.label import (
    LabelResponse,
    LabelCreateRequest,
    LabelUpdateRequest,
)
from petos_api.schemas.dependency import (
    DependencyResponse,
    DependencyCreateRequest,
)
from petos_api.schemas.activity import ActivityResponse
from petos_api.schemas.user import OrganizationMemberResponse
from petos_api.core.errors import AppError


class TaskService:
    ALLOWED_TRANSITIONS = {
        "backlog": {"ready", "cancelled"},
        "ready": {"in_progress", "backlog", "cancelled"},
        "in_progress": {"blocked", "review", "cancelled"},
        "blocked": {"in_progress", "cancelled"},
        "review": {"in_progress", "completed", "cancelled"},
        "completed": {"in_progress"},
        "cancelled": {"backlog"},
    }

    def __init__(self, session: AsyncSession):
        self.db_session = session
        self.task_repo = TaskRepository(session)
        self.comment_repo = CommentRepository(session)
        self.label_repo = LabelRepository(session)
        self.dependency_repo = DependencyRepository(session)
        self.activity_repo = ActivityRepository(session)
        self.project_repo = ProjectRepository(session)
        self.membership_repo = MembershipRepository(session)
        self.user_repo = UserRepository(session)

    async def _require_project_access(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        required_roles: Optional[List[str]] = None,
    ) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise AppError(
                status_code=404, code="not_found", message="Project not found"
            )

        membership = await self.membership_repo.get_membership(
            user_id, project.organization_id
        )
        if not membership:
            raise AppError(
                status_code=404, code="not_found", message="Project not found"
            )

        if required_roles and membership.role not in required_roles:
            raise AppError(
                status_code=403, code="forbidden", message="Insufficient permissions"
            )

        return project

    async def _log_activity(
        self,
        task_id: uuid.UUID,
        actor_id: uuid.UUID,
        event_type: str,
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        extra_meta: Optional[Dict] = None,
    ) -> None:
        meta = {"schema_version": 1}
        if extra_meta:
            meta.update(extra_meta)
        activity = TaskActivity(
            id=uuid.uuid4(),
            task_id=task_id,
            actor_id=actor_id,
            event_type=event_type,
            previous_value=previous_value,
            new_value=new_value,
            metadata_json=meta,
            created_at=datetime.now(timezone.utc),
        )
        self.activity_repo.add(activity)

    async def _build_task_response(self, task: Task, project_key: str) -> TaskResponse:
        labels = await self.task_repo.get_labels_for_task(task.id)
        label_responses = [
            LabelResponse(
                id=lbl.id,
                project_id=lbl.project_id,
                name=lbl.name,
                slug=lbl.slug,
                color=lbl.color,
                version=lbl.version,
                created_at=lbl.created_at,
                updated_at=lbl.updated_at,
            )
            for lbl in labels
        ]
        unresolved = await self.dependency_repo.get_unresolved_dependencies_for_task(
            task.id
        )
        display_id = f"{project_key}-{task.task_number}"

        return TaskResponse(
            id=task.id,
            project_id=task.project_id,
            project_key=project_key,
            task_number=task.task_number,
            display_id=display_id,
            title=task.title,
            description=task.description,
            acceptance_criteria=task.acceptance_criteria,
            status=task.status,
            priority=task.priority,
            created_by=task.created_by,
            assigned_to=task.assigned_to,
            due_at=task.due_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            archived_at=task.archived_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            version=task.version,
            labels=label_responses,
            unresolved_dependency_count=len(unresolved),
        )

    async def create_task(
        self, user_id: uuid.UUID, project_id: uuid.UUID, req: TaskCreateRequest
    ) -> TaskResponse:
        project = await self._require_project_access(
            user_id, project_id, required_roles=["owner", "admin", "member"]
        )

        if req.assigned_to:
            assignee_mem = await self.membership_repo.get_membership(
                req.assigned_to, project.organization_id
            )
            if not assignee_mem:
                raise AppError(
                    status_code=400,
                    code="invalid_assignee",
                    message="Assignee must be a member of the organization",
                )

        # Atomic number allocation
        task_num = await self.project_repo.allocate_next_task_number(project_id)

        task = Task(
            id=uuid.uuid4(),
            project_id=project_id,
            task_number=task_num,
            title=req.title.strip(),
            description=req.description,
            acceptance_criteria=req.acceptance_criteria,
            status="backlog",
            priority=req.priority,
            created_by=user_id,
            assigned_to=req.assigned_to,
            due_at=req.due_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=1,
        )
        self.task_repo.add(task)

        if req.label_ids:
            await self.task_repo.set_task_labels(task.id, req.label_ids)

        await self._log_activity(
            task_id=task.id,
            actor_id=user_id,
            event_type="task.created",
            new_value=f"{project.key}-{task_num}",
            extra_meta={"title": task.title},
        )

        await self.db_session.commit()
        await self.db_session.refresh(task)
        return await self._build_task_response(task, project.key)

    async def get_task(self, user_id: uuid.UUID, task_id: uuid.UUID) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(user_id, task.project_id)
        return await self._build_task_response(task, project.key)

    async def update_task(
        self, user_id: uuid.UUID, task_id: uuid.UUID, req: TaskUpdateRequest
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        if req.assigned_to:
            assignee_mem = await self.membership_repo.get_membership(
                req.assigned_to, project.organization_id
            )
            if not assignee_mem:
                raise AppError(
                    status_code=400,
                    code="invalid_assignee",
                    message="Assignee must be a member of the organization",
                )

        success = await self.task_repo.update_task_fields(
            task_id=task_id,
            expected_version=req.expected_version,
            title=req.title.strip() if req.title else None,
            description=req.description,
            acceptance_criteria=req.acceptance_criteria,
            priority=req.priority,
            assigned_to=req.assigned_to,
            due_at=req.due_at,
        )

        if not success:
            raise AppError(
                status_code=409,
                code="concurrency_conflict",
                message="Task was modified by another user",
            )

        await self._log_activity(
            task_id=task_id,
            actor_id=user_id,
            event_type="task.updated",
            extra_meta={"updated_version": req.expected_version + 1},
        )

        await self.db_session.commit()
        refreshed = await self.task_repo.get_by_id(task_id)
        assert refreshed is not None
        return await self._build_task_response(refreshed, project.key)

    async def transition_task(
        self, user_id: uuid.UUID, task_id: uuid.UUID, req: TaskTransitionRequest
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        current_status = task.status
        target_status = req.target_status

        if target_status not in self.ALLOWED_TRANSITIONS.get(current_status, set()):
            raise AppError(
                status_code=400,
                code="invalid_transition",
                message=f"Cannot transition task from '{current_status}' to '{target_status}'",
            )

        # Reopen reason validation
        if (current_status == "completed" and target_status == "in_progress") or (
            current_status == "cancelled" and target_status == "backlog"
        ):
            if not req.reason or not req.reason.strip():
                raise AppError(
                    status_code=400,
                    code="transition_reason_required",
                    message=f"A reason is required when transitioning from {current_status} to {target_status}",
                )

        # Completion prerequisite check
        if target_status == "completed":
            unresolved = (
                await self.dependency_repo.get_unresolved_dependencies_for_task(task_id)
            )
            if unresolved:
                unresolved_ids = [str(u.id) for u in unresolved]
                unresolved_displays = [
                    f"{project.key}-{u.task_number}" for u in unresolved
                ]
                raise AppError(
                    status_code=409,
                    code="unresolved_dependencies",
                    message=f"Cannot complete task with unresolved dependencies: {', '.join(unresolved_displays)}",
                )

        now = datetime.now(timezone.utc)
        started_at = None
        completed_at = None
        clear_completed_at = False

        if target_status == "in_progress" and task.started_at is None:
            started_at = now

        if target_status == "completed":
            completed_at = now
        elif current_status == "completed":
            clear_completed_at = True

        success = await self.task_repo.update_status(
            task_id=task_id,
            expected_version=req.expected_version,
            target_status=target_status,
            started_at=started_at,
            completed_at=completed_at,
            clear_completed_at=clear_completed_at,
        )

        if not success:
            raise AppError(
                status_code=409,
                code="concurrency_conflict",
                message="Task was modified by another user",
            )

        meta = {"reason": req.reason} if req.reason else {}
        await self._log_activity(
            task_id=task_id,
            actor_id=user_id,
            event_type="task.transitioned",
            previous_value=current_status,
            new_value=target_status,
            extra_meta=meta,
        )

        await self.db_session.commit()
        refreshed = await self.task_repo.get_by_id(task_id)
        assert refreshed is not None
        return await self._build_task_response(refreshed, project.key)

    async def archive_task(
        self, user_id: uuid.UUID, task_id: uuid.UUID, req: TaskArchiveRequest
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin"]
        )

        if task.archived_at is not None:
            return await self._build_task_response(task, project.key)

        success = await self.task_repo.archive_task(task_id, req.expected_version)
        if not success:
            raise AppError(
                status_code=409,
                code="concurrency_conflict",
                message="Task was modified by another user",
            )

        meta = {"reason": req.reason} if req.reason else {}
        await self._log_activity(
            task_id=task_id,
            actor_id=user_id,
            event_type="task.archived",
            extra_meta=meta,
        )

        await self.db_session.commit()
        refreshed = await self.task_repo.get_by_id(task_id)
        assert refreshed is not None
        return await self._build_task_response(refreshed, project.key)

    async def get_tasks(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        statuses: Optional[List[str]] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[uuid.UUID] = None,
        label: Optional[str] = None,
        search: Optional[str] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        include_archived: bool = False,
        sort: str = "-created_at",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[TaskResponse], int]:
        project = await self._require_project_access(user_id, project_id)
        tasks, total = await self.task_repo.query_tasks(
            project_id=project_id,
            statuses=statuses,
            priority=priority,
            assigned_to=assigned_to,
            label_id_or_slug=label,
            search_query=search,
            due_before=due_before,
            due_after=due_after,
            include_archived=include_archived,
            sort_by=sort,
            limit=limit,
            offset=offset,
        )
        responses = [await self._build_task_response(t, project.key) for t in tasks]
        return responses, total

    async def get_board_view(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> BoardViewResponse:
        project = await self._require_project_access(user_id, project_id)
        all_statuses = [
            "backlog",
            "ready",
            "in_progress",
            "blocked",
            "review",
            "completed",
            "cancelled",
        ]
        columns = []

        for status in all_statuses:
            tasks, total = await self.task_repo.query_tasks(
                project_id=project_id,
                statuses=[status],
                include_archived=False,
                limit=50,
                offset=0,
            )
            item_resps = [
                await self._build_task_response(t, project.key) for t in tasks
            ]
            columns.append(
                BoardColumnResponse(
                    status=status,
                    items=item_resps,
                    total=total,
                    returned_count=len(item_resps),
                    has_more=total > len(item_resps),
                )
            )

        return BoardViewResponse(columns=columns)

    # Comments
    async def add_comment(
        self, user_id: uuid.UUID, task_id: uuid.UUID, req: CommentCreateRequest
    ) -> CommentResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        comment = TaskComment(
            id=uuid.uuid4(),
            task_id=task_id,
            author_id=user_id,
            body=req.body.strip(),
            version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.comment_repo.add(comment)

        await self._log_activity(
            task_id=task_id,
            actor_id=user_id,
            event_type="comment.created",
            extra_meta={"comment_id": str(comment.id)},
        )

        await self.db_session.commit()
        await self.db_session.refresh(comment)

        return CommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            body=comment.body,
            version=comment.version,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    async def update_comment(
        self, user_id: uuid.UUID, comment_id: uuid.UUID, req: CommentUpdateRequest
    ) -> CommentResponse:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise AppError(
                status_code=404, code="not_found", message="Comment not found"
            )

        task = await self.task_repo.get_by_id(comment.task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        if comment.author_id != user_id:
            raise AppError(
                status_code=403,
                code="comment_not_owned",
                message="Cannot edit another user's comment",
            )

        success = await self.comment_repo.update_comment(
            comment_id=comment_id,
            expected_version=req.expected_version,
            body=req.body.strip(),
        )

        if not success:
            raise AppError(
                status_code=409,
                code="concurrency_conflict",
                message="Comment was modified by another user",
            )

        await self._log_activity(
            task_id=comment.task_id,
            actor_id=user_id,
            event_type="comment.updated",
            extra_meta={"comment_id": str(comment_id)},
        )

        await self.db_session.commit()
        refreshed = await self.comment_repo.get_by_id(comment_id)
        assert refreshed is not None

        return CommentResponse(
            id=refreshed.id,
            task_id=refreshed.task_id,
            author_id=refreshed.author_id,
            body=refreshed.body,
            version=refreshed.version,
            created_at=refreshed.created_at,
            updated_at=refreshed.updated_at,
        )

    async def get_comments(
        self, user_id: uuid.UUID, task_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[CommentResponse], int]:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        await self._require_project_access(user_id, task.project_id)
        comments, total = await self.comment_repo.get_comments_for_task(
            task_id, limit, offset
        )

        responses = [
            CommentResponse(
                id=c.id,
                task_id=c.task_id,
                author_id=c.author_id,
                body=c.body,
                version=c.version,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in comments
        ]
        return responses, total

    # Labels
    async def create_label(
        self, user_id: uuid.UUID, project_id: uuid.UUID, req: LabelCreateRequest
    ) -> LabelResponse:
        await self._require_project_access(
            user_id, project_id, required_roles=["owner", "admin", "member"]
        )

        slug = re.sub(r"[^a-z0-9]+", "-", req.name.lower()).strip("-")
        if not slug:
            slug = "label"

        existing = await self.label_repo.get_by_slug(project_id, slug)
        if existing:
            raise AppError(
                status_code=409,
                code="label_conflict",
                message=f"Label with name/slug '{req.name}' already exists",
            )

        label = Label(
            id=uuid.uuid4(),
            project_id=project_id,
            name=req.name.strip(),
            slug=slug,
            color=req.color,
            version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.label_repo.add(label)
        await self.db_session.commit()
        await self.db_session.refresh(label)

        return LabelResponse(
            id=label.id,
            project_id=label.project_id,
            name=label.name,
            slug=label.slug,
            color=label.color,
            version=label.version,
            created_at=label.created_at,
            updated_at=label.updated_at,
        )

    async def update_label(
        self, user_id: uuid.UUID, label_id: uuid.UUID, req: LabelUpdateRequest
    ) -> LabelResponse:
        label = await self.label_repo.get_by_id(label_id)
        if not label:
            raise AppError(status_code=404, code="not_found", message="Label not found")

        await self._require_project_access(
            user_id, label.project_id, required_roles=["owner", "admin", "member"]
        )

        slug = re.sub(r"[^a-z0-9]+", "-", req.name.lower()).strip("-")
        if not slug:
            slug = "label"

        existing = await self.label_repo.get_by_slug(label.project_id, slug)
        if existing and existing.id != label_id:
            raise AppError(
                status_code=409,
                code="label_conflict",
                message=f"Label with name '{req.name}' already exists",
            )

        success = await self.label_repo.update_label(
            label_id=label_id,
            expected_version=req.expected_version,
            name=req.name.strip(),
            slug=slug,
            color=req.color,
        )

        if not success:
            raise AppError(
                status_code=409,
                code="concurrency_conflict",
                message="Label was modified by another user",
            )

        await self.db_session.commit()
        refreshed = await self.label_repo.get_by_id(label_id)
        assert refreshed is not None

        return LabelResponse(
            id=refreshed.id,
            project_id=refreshed.project_id,
            name=refreshed.name,
            slug=refreshed.slug,
            color=refreshed.color,
            version=refreshed.version,
            created_at=refreshed.created_at,
            updated_at=refreshed.updated_at,
        )

    async def get_labels(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[LabelResponse], int]:
        await self._require_project_access(
            user_id, project_id, required_roles=["owner", "admin", "member", "viewer"]
        )
        labels, total = await self.label_repo.get_labels_for_project(
            project_id, limit, offset
        )
        responses = [
            LabelResponse(
                id=lbl.id,
                project_id=lbl.project_id,
                name=lbl.name,
                slug=lbl.slug,
                color=lbl.color,
                version=lbl.version,
                created_at=lbl.created_at,
                updated_at=lbl.updated_at,
            )
            for lbl in labels
        ]
        return responses, total

    async def add_task_label(
        self, user_id: uuid.UUID, task_id: uuid.UUID, label_id: uuid.UUID
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        label = await self.label_repo.get_by_id(label_id)
        if not label:
            raise AppError(status_code=404, code="not_found", message="Label not found")

        if label.project_id != task.project_id:
            raise AppError(
                status_code=400,
                code="cross_project_label_rejected",
                message="Label must belong to the same project",
            )

        existing_labels = await self.task_repo.get_labels_for_task(task_id)
        if label_id not in [lbl.id for lbl in existing_labels]:
            new_ids = [lbl.id for lbl in existing_labels] + [label_id]
            await self.task_repo.set_task_labels(task_id, new_ids)
            await self._log_activity(
                task_id=task_id,
                actor_id=user_id,
                event_type="label.added",
                extra_meta={"label_name": label.name},
            )
            await self.db_session.commit()

        refreshed = await self.task_repo.get_by_id(task_id)
        assert refreshed is not None
        return await self._build_task_response(refreshed, project.key)

    async def remove_task_label(
        self, user_id: uuid.UUID, task_id: uuid.UUID, label_id: uuid.UUID
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        label = await self.label_repo.get_by_id(label_id)
        existing_labels = await self.task_repo.get_labels_for_task(task_id)

        if label_id in [lbl.id for lbl in existing_labels]:
            new_ids = [lbl.id for lbl in existing_labels if lbl.id != label_id]
            await self.task_repo.set_task_labels(task_id, new_ids)
            await self._log_activity(
                task_id=task_id,
                actor_id=user_id,
                event_type="label.removed",
                extra_meta={"label_name": label.name if label else "unknown"},
            )
            await self.db_session.commit()

        refreshed = await self.task_repo.get_by_id(task_id)
        assert refreshed is not None
        return await self._build_task_response(refreshed, project.key)

    # Dependencies & Advisory Lock Cycle Detection
    async def add_dependency(
        self, user_id: uuid.UUID, task_id: uuid.UUID, req: DependencyCreateRequest
    ) -> DependencyResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        if task_id == req.depends_on_task_id:
            raise AppError(
                status_code=400,
                code="self_dependency_rejected",
                message="A task cannot depend on itself",
            )

        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        depends_on_id = req.depends_on_task_id
        target_task = await self.task_repo.get_by_id(depends_on_id)
        if not target_task or target_task.project_id != task.project_id:
            raise AppError(
                status_code=400,
                code="cross_project_dependency_rejected",
                message="Target task must belong to the same project",
            )

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        # PostgreSQL transaction-level advisory lock on project_id
        await self.dependency_repo.acquire_project_advisory_lock(task.project_id)

        # Check duplicate
        existing_pair = await self.dependency_repo.get_by_pair(task_id, depends_on_id)
        if existing_pair:
            raise AppError(
                status_code=400,
                code="duplicate_dependency",
                message="Dependency already exists",
            )

        # Re-read all project dependencies for graph cycle check
        all_deps = await self.dependency_repo.get_all_project_dependencies(
            task.project_id
        )
        graph: Dict[uuid.UUID, Set[uuid.UUID]] = {}
        for d in all_deps:
            graph.setdefault(d.task_id, set()).add(d.depends_on_task_id)

        # Add proposed edge: task_id -> depends_on_id
        graph.setdefault(task_id, set()).add(depends_on_id)

        # Cycle check via DFS: Check if depends_on_id can reach task_id
        visited: Set[uuid.UUID] = set()
        stack: Set[uuid.UUID] = set()

        def has_path(curr: uuid.UUID, target: uuid.UUID) -> bool:
            if curr == target:
                return True
            visited.add(curr)
            stack.add(curr)
            for nxt in graph.get(curr, set()):
                if nxt not in visited:
                    if has_path(nxt, target):
                        return True
                elif nxt in stack:
                    return True
            stack.remove(curr)
            return False

        if has_path(depends_on_id, task_id):
            raise AppError(
                status_code=400,
                code="circular_dependency_detected",
                message="Adding this dependency creates a circular dependency cycle",
            )

        dep = TaskDependency(
            id=uuid.uuid4(),
            task_id=task_id,
            depends_on_task_id=depends_on_id,
            created_by=user_id,
            created_at=datetime.now(timezone.utc),
        )
        self.dependency_repo.add(dep)

        target_display = f"{project.key}-{target_task.task_number}"
        await self._log_activity(
            task_id=task_id,
            actor_id=user_id,
            event_type="dependency.added",
            new_value=target_display,
        )

        await self.db_session.commit()
        await self.db_session.refresh(dep)

        return DependencyResponse(
            id=dep.id,
            task_id=dep.task_id,
            depends_on_task_id=dep.depends_on_task_id,
            depends_on_display_id=target_display,
            created_by=dep.created_by,
            created_at=dep.created_at,
        )

    async def remove_dependency(
        self, user_id: uuid.UUID, task_id: uuid.UUID, dependency_id: uuid.UUID
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(
            user_id, task.project_id, required_roles=["owner", "admin", "member"]
        )

        if task.archived_at is not None:
            raise AppError(
                status_code=409,
                code="task_archived",
                message="Archived task is read-only",
            )

        dep = await self.dependency_repo.get_by_id(dependency_id)
        if dep and dep.task_id == task_id:
            await self.dependency_repo.delete(dependency_id)
            await self._log_activity(
                task_id=task_id,
                actor_id=user_id,
                event_type="dependency.removed",
                extra_meta={"dependency_id": str(dependency_id)},
            )
            await self.db_session.commit()

        refreshed = await self.task_repo.get_by_id(task_id)
        assert refreshed is not None
        return await self._build_task_response(refreshed, project.key)

    async def get_dependencies(
        self, user_id: uuid.UUID, task_id: uuid.UUID
    ) -> List[DependencyResponse]:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        project = await self._require_project_access(user_id, task.project_id)
        deps = await self.dependency_repo.get_dependencies_for_task(task_id)

        responses = []
        for d in deps:
            target_task = await self.task_repo.get_by_id(d.depends_on_task_id)
            display_id = (
                f"{project.key}-{target_task.task_number}" if target_task else "UNKNOWN"
            )
            responses.append(
                DependencyResponse(
                    id=d.id,
                    task_id=d.task_id,
                    depends_on_task_id=d.depends_on_task_id,
                    depends_on_display_id=display_id,
                    created_by=d.created_by,
                    created_at=d.created_at,
                )
            )

        return responses

    # Activities
    async def get_activities(
        self, user_id: uuid.UUID, task_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[ActivityResponse], int]:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise AppError(status_code=404, code="not_found", message="Task not found")

        await self._require_project_access(user_id, task.project_id)
        activities, total = await self.activity_repo.get_activities_for_task(
            task_id, limit, offset
        )

        responses = [
            ActivityResponse(
                id=a.id,
                task_id=a.task_id,
                actor_id=a.actor_id,
                event_type=a.event_type,
                previous_value=a.previous_value,
                new_value=a.new_value,
                metadata=a.metadata_json or {},
                created_at=a.created_at,
            )
            for a in activities
        ]
        return responses, total

    # Organization Member Discovery Endpoint Service Method
    async def get_organization_members(
        self, user_id: uuid.UUID, org_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> Tuple[List[OrganizationMemberResponse], int]:
        # Validate active user membership in organization
        membership = await self.membership_repo.get_membership(user_id, org_id)
        if not membership:
            raise AppError(
                status_code=404, code="not_found", message="Organization not found"
            )

        from petos_api.models.organization_membership import OrganizationMembership
        from petos_api.models.user import User
        from sqlalchemy import select, func

        count_stmt = select(func.count(OrganizationMembership.id)).where(
            OrganizationMembership.organization_id == org_id
        )
        total = await self.db_session.scalar(count_stmt) or 0

        stmt = (
            select(OrganizationMembership, User)
            .join(User, User.id == OrganizationMembership.user_id)
            .where(OrganizationMembership.organization_id == org_id)
            .order_by(User.display_name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db_session.execute(stmt)
        rows = result.all()

        responses = [
            OrganizationMemberResponse(
                user_id=u.id,
                display_name=u.display_name,
                role=m.role,
                status=u.status,
            )
            for m, u in rows
        ]
        return responses, total
