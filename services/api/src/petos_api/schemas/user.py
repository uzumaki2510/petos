from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
import uuid


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str
    status: str
    created_at: datetime
    updated_at: datetime


class OrganizationMemberResponse(BaseModel):
    user_id: uuid.UUID
    display_name: str
    role: str
    status: str


class PaginatedOrganizationMemberResponse(BaseModel):
    items: List[OrganizationMemberResponse]
    limit: int
    offset: int
    total: int
