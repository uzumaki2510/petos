from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, Index, DateTime
from .base import Base
import uuid
from datetime import datetime


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    depends_on_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )

    __table_args__ = (
        UniqueConstraint(
            "task_id", "depends_on_task_id", name="uq_task_dependencies_pair"
        ),
        CheckConstraint(
            "task_id <> depends_on_task_id", name="ck_task_dependencies_no_self"
        ),
        Index("idx_task_deps_task", "task_id"),
        Index("idx_task_deps_target", "depends_on_task_id"),
    )
