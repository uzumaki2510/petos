from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from .base import Base
import uuid


class TaskLabel(Base):
    __tablename__ = "task_labels"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    label_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("labels.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
