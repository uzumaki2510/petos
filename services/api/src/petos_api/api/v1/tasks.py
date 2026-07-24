from typing import Optional, List
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.api.dependencies.auth import get_current_user
from petos_api.models.user import User
from petos_api.services.task_service import TaskService
from petos_api.schemas.task import (
    TaskResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskTransitionRequest,
    TaskArchiveRequest,
    PaginatedTaskResponse,
    BoardViewResponse,
)
from petos_api.schemas.comment import (
    CommentResponse,
    CommentCreateRequest,
    PaginatedCommentResponse,
)
from petos_api.schemas.dependency import (
    DependencyResponse,
    DependencyCreateRequest,
)
from petos_api.schemas.activity import PaginatedActivityResponse

router = APIRouter(tags=["tasks"])


@router.get(
    "/v1/projects/{project_id}/tasks",
    response_model=PaginatedTaskResponse,
)
async def list_tasks(
    project_id: uuid.UUID = Path(...),
    status: Optional[str] = Query(
        None, description="Comma-separated or repeated status values"
    ),
    priority: Optional[str] = Query(None, pattern=r"^(low|medium|high|urgent)$"),
    assigned_to: Optional[uuid.UUID] = Query(None),
    label: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    include_archived: bool = Query(False),
    sort: str = Query(
        "-created_at",
        pattern=r"^-(created_at|updated_at|due_at|task_number)|(created_at|updated_at|due_at|priority|task_number)$",
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    status_list = [s.strip() for s in status.split(",")] if status else None
    items, total = await service.get_tasks(
        user_id=user.id,
        project_id=project_id,
        statuses=status_list,
        priority=priority,
        assigned_to=assigned_to,
        label=label,
        search=search,
        due_before=due_before,
        due_after=due_after,
        include_archived=include_archived,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return PaginatedTaskResponse(items=items, limit=limit, offset=offset, total=total)


@router.post(
    "/v1/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=201,
)
async def create_task(
    req: TaskCreateRequest,
    project_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.create_task(user.id, project_id, req)


@router.get(
    "/v1/projects/{project_id}/board",
    response_model=BoardViewResponse,
)
async def get_board_view(
    project_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.get_board_view(user.id, project_id)


@router.get(
    "/v1/tasks/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.get_task(user.id, task_id)


@router.patch(
    "/v1/tasks/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    req: TaskUpdateRequest,
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.update_task(user.id, task_id, req)


@router.post(
    "/v1/tasks/{task_id}/transition",
    response_model=TaskResponse,
)
async def transition_task(
    req: TaskTransitionRequest,
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.transition_task(user.id, task_id, req)


@router.post(
    "/v1/tasks/{task_id}/archive",
    response_model=TaskResponse,
)
async def archive_task(
    req: TaskArchiveRequest,
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.archive_task(user.id, task_id, req)


# Comments
@router.get(
    "/v1/tasks/{task_id}/comments",
    response_model=PaginatedCommentResponse,
)
async def list_comments(
    task_id: uuid.UUID = Path(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    items, total = await service.get_comments(user.id, task_id, limit, offset)
    return PaginatedCommentResponse(
        items=items, limit=limit, offset=offset, total=total
    )


@router.post(
    "/v1/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=201,
)
async def add_comment(
    req: CommentCreateRequest,
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.add_comment(user.id, task_id, req)


# Dependencies
@router.get(
    "/v1/tasks/{task_id}/dependencies",
    response_model=List[DependencyResponse],
)
async def list_dependencies(
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.get_dependencies(user.id, task_id)


@router.post(
    "/v1/tasks/{task_id}/dependencies",
    response_model=DependencyResponse,
    status_code=201,
)
async def add_dependency(
    req: DependencyCreateRequest,
    task_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.add_dependency(user.id, task_id, req)


@router.delete(
    "/v1/tasks/{task_id}/dependencies/{dependency_id}",
    response_model=TaskResponse,
)
async def remove_dependency(
    task_id: uuid.UUID = Path(...),
    dependency_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.remove_dependency(user.id, task_id, dependency_id)


# Activities
@router.get(
    "/v1/tasks/{task_id}/activity",
    response_model=PaginatedActivityResponse,
)
async def list_activities(
    task_id: uuid.UUID = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    items, total = await service.get_activities(user.id, task_id, limit, offset)
    return PaginatedActivityResponse(
        items=items, limit=limit, offset=offset, total=total
    )
