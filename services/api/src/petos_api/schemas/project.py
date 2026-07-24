from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class ProjectResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    key: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    key: Optional[str] = Field(
        None,
        pattern=r"^[A-Z][A-Z0-9]{1,9}$",
        description="Immutable 2-10 char project key e.g. PET",
    )
    description: Optional[str] = Field(None, max_length=1000)


class ProjectUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
