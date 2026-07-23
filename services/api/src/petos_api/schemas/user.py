from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    display_name: str
    status: str
    created_at: datetime
    updated_at: datetime
