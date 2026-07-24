import uuid
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.api.dependencies.auth import get_current_user
from petos_api.models.user import User
from petos_api.services.task_service import TaskService
from petos_api.schemas.label import (
    LabelResponse,
    LabelCreateRequest,
    LabelUpdateRequest,
    PaginatedLabelResponse,
)
from petos_api.schemas.task import TaskResponse

router = APIRouter(tags=["labels"])


@router.get(
    "/v1/projects/{project_id}/labels",
    response_model=PaginatedLabelResponse,
)
async def list_labels(
    project_id: uuid.UUID = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    items, total = await service.get_labels(user.id, project_id, limit, offset)
    return PaginatedLabelResponse(items=items, limit=limit, offset=offset, total=total)


@router.post(
    "/v1/projects/{project_id}/labels",
    response_model=LabelResponse,
    status_code=201,
)
async def create_label(
    req: LabelCreateRequest,
    project_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.create_label(user.id, project_id, req)


@router.patch(
    "/v1/labels/{label_id}",
    response_model=LabelResponse,
)
async def update_label(
    req: LabelUpdateRequest,
    label_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.update_label(user.id, label_id, req)


@router.post(
    "/v1/tasks/{task_id}/labels/{label_id}",
    response_model=TaskResponse,
)
async def add_task_label(
    task_id: uuid.UUID = Path(...),
    label_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.add_task_label(user.id, task_id, label_id)


@router.delete(
    "/v1/tasks/{task_id}/labels/{label_id}",
    response_model=TaskResponse,
)
async def remove_task_label(
    task_id: uuid.UUID = Path(...),
    label_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.remove_task_label(user.id, task_id, label_id)
