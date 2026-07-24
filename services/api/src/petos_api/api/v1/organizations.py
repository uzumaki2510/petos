from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from petos_api.schemas.user import PaginatedOrganizationMemberResponse
from petos_api.schemas.pagination import PaginatedOrganizationResponse
from petos_api.services.organization_service import OrganizationService
from petos_api.services.task_service import TaskService
from petos_api.api.dependencies.auth import get_current_user
from petos_api.models.user import User
import uuid

router = APIRouter()


@router.get("", response_model=PaginatedOrganizationResponse)
async def get_organizations(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    org_service = OrganizationService(db)
    items, total = await org_service.get_user_organizations(user.id, limit, offset)
    return PaginatedOrganizationResponse(
        items=items, limit=limit, offset=offset, total=total
    )


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_service = OrganizationService(db)
    return await org_service.get_organization(user.id, organization_id)


@router.get(
    "/{organization_id}/members", response_model=PaginatedOrganizationMemberResponse
)
async def get_organization_members(
    organization_id: uuid.UUID = Path(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TaskService(db)
    items, total = await service.get_organization_members(
        user.id, organization_id, limit, offset
    )
    return PaginatedOrganizationMemberResponse(
        items=items, limit=limit, offset=offset, total=total
    )


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: uuid.UUID,
    req: OrganizationUpdateRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_service = OrganizationService(db)
    return await org_service.update_organization(user.id, organization_id, req)
