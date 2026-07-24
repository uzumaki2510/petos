from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from .base import Base, TimestampMixin
import uuid


class Label(Base, TimestampMixin):
    __tablename__ = "labels"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False, default="#6B7280")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_labels_project_slug"),
        CheckConstraint("version >= 1", name="ck_labels_version"),
        CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="ck_labels_color_hex"),
        Index("idx_labels_project", "project_id"),
    )
