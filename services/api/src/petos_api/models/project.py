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


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(10), nullable=False)
    next_task_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id", "slug", name="uq_projects_organization_slug"
        ),
        UniqueConstraint("organization_id", "key", name="uq_projects_organization_key"),
        CheckConstraint(
            "key ~ '^[A-Z][A-Z0-9]{1,9}$'", name="projects_key_format_check"
        ),
        CheckConstraint(
            status.in_(["active", "archived"]), name="projects_status_check"
        ),
        Index("idx_projects_org_status", "organization_id", "status"),
    )
