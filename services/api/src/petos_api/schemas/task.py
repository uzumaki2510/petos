from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from petos_api.schemas.label import LabelResponse


class TaskResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_key: str
    task_number: int
    display_id: str
    title: str
    description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    status: str
    priority: str
    created_by: uuid.UUID
    assigned_to: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int
    labels: List[LabelResponse] = Field(default_factory=list)
    unresolved_dependency_count: int = 0


class TaskSummaryResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_key: str
    task_number: int
    display_id: str
    title: str
    status: str
    priority: str
    assigned_to: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    version: int


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=50000)
    acceptance_criteria: Optional[str] = Field(None, max_length=50000)
    priority: str = Field("medium", pattern=r"^(low|medium|high|urgent)$")
    assigned_to: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None
    label_ids: List[uuid.UUID] = Field(default_factory=list)


class TaskUpdateRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=50000)
    acceptance_criteria: Optional[str] = Field(None, max_length=50000)
    priority: Optional[str] = Field(None, pattern=r"^(low|medium|high|urgent)$")
    assigned_to: Optional[uuid.UUID] = None
    due_at: Optional[datetime] = None


class TaskTransitionRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    target_status: str = Field(
        ..., pattern=r"^(backlog|ready|in_progress|blocked|review|completed|cancelled)$"
    )
    reason: Optional[str] = Field(None, max_length=2000)


class TaskArchiveRequest(BaseModel):
    expected_version: int = Field(..., ge=1)
    reason: Optional[str] = Field(None, max_length=2000)


class PaginatedTaskResponse(BaseModel):
    items: List[TaskResponse]
    limit: int
    offset: int
    total: int


class BoardColumnResponse(BaseModel):
    status: str
    items: List[TaskResponse]
    total: int
    returned_count: int
    has_more: bool


class BoardViewResponse(BaseModel):
    columns: List[BoardColumnResponse]
