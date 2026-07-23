from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class OrganizationUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
