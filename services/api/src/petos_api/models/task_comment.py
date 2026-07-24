from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, ForeignKey, CheckConstraint, Index
from .base import Base, TimestampMixin
import uuid


class TaskComment(Base, TimestampMixin):
    __tablename__ = "task_comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_task_comments_version"),
        CheckConstraint(
            "length(trim(body)) > 0", name="ck_task_comments_body_nonempty"
        ),
        Index("idx_task_comments_task_created", "task_id", "created_at"),
    )
