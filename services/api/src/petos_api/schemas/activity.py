from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ActivityResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    actor_id: uuid.UUID
    event_type: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class PaginatedActivityResponse(BaseModel):
    items: List[ActivityResponse]
    limit: int
    offset: int
    total: int
