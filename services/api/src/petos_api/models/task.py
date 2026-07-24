from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    DateTime,
)
from .base import Base, TimestampMixin
import uuid
from datetime import datetime


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    task_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="backlog")
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("project_id", "task_number", name="uq_tasks_project_number"),
        CheckConstraint("version >= 1", name="ck_tasks_version"),
        CheckConstraint(
            "status IN ('backlog', 'ready', 'in_progress', 'blocked', 'review', 'completed', 'cancelled')",
            name="ck_tasks_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name="ck_tasks_priority",
        ),
        CheckConstraint("length(trim(title)) > 0", name="ck_tasks_title_nonempty"),
        Index("idx_tasks_project_status", "project_id", "status"),
        Index("idx_tasks_project_assignee", "project_id", "assigned_to"),
        Index("idx_tasks_project_created", "project_id", "created_at"),
    )
