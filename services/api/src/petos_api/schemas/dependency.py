from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid


class DependencyResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    depends_on_task_id: uuid.UUID
    depends_on_display_id: str
    created_by: uuid.UUID
    created_at: datetime


class DependencyCreateRequest(BaseModel):
    depends_on_task_id: uuid.UUID


class PaginatedDependencyResponse(BaseModel):
    items: List[DependencyResponse]
    limit: int
    offset: int
    total: int
