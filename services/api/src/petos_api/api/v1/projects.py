from fastapi import APIRouter, Depends, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.schemas.project import (
    ProjectResponse,
    ProjectCreateRequest,
    ProjectUpdateRequest,
)
from petos_api.schemas.pagination import PaginatedProjectResponse
from petos_api.services.project_service import ProjectService
from petos_api.api.dependencies.auth import get_current_user
from petos_api.models.user import User
import uuid

router = APIRouter()


@router.get(
    "/organizations/{organization_id}/projects", response_model=PaginatedProjectResponse
)
async def get_projects(
    organization_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    project_service = ProjectService(db)
    items, total = await project_service.get_projects(
        user.id, organization_id, limit, offset
    )
    return PaginatedProjectResponse(
        items=items, limit=limit, offset=offset, total=total
    )


@router.post(
    "/organizations/{organization_id}/projects",
    response_model=ProjectResponse,
    status_code=201,
)
async def create_project(
    organization_id: uuid.UUID,
    req: ProjectCreateRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_service = ProjectService(db)
    return await project_service.create_project(user.id, organization_id, req)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_service = ProjectService(db)
    return await project_service.get_project(user.id, project_id)


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    req: ProjectUpdateRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_service = ProjectService(db)
    return await project_service.update_project(user.id, project_id, req)


@router.post("/projects/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_service = ProjectService(db)
    return await project_service.archive_project(user.id, project_id)
