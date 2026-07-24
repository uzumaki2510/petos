from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid


class LabelResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    slug: str
    color: str
    version: int
    created_at: datetime
    updated_at: datetime


class LabelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field("#6B7280", pattern=r"^#[0-9A-Fa-f]{6}$")


class LabelUpdateRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")


class PaginatedLabelResponse(BaseModel):
    items: List[LabelResponse]
    limit: int
    offset: int
    total: int
