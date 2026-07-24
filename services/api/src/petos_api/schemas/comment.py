from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid


class CommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    author_id: uuid.UUID
    body: str
    version: int
    created_at: datetime
    updated_at: datetime


class CommentCreateRequest(BaseModel):
    body: str = Field(..., min_length=1, max_length=10000)


class CommentUpdateRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    body: str = Field(..., min_length=1, max_length=10000)


class PaginatedCommentResponse(BaseModel):
    items: List[CommentResponse]
    limit: int
    offset: int
    total: int
