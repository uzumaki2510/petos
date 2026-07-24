import uuid
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.api.dependencies.auth import get_current_user
from petos_api.models.user import User
from petos_api.services.task_service import TaskService
from petos_api.schemas.comment import CommentResponse, CommentUpdateRequest

router = APIRouter(tags=["comments"])


@router.patch(
    "/v1/task-comments/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    req: CommentUpdateRequest,
    comment_id: uuid.UUID = Path(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.update_comment(user.id, comment_id, req)
