from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, CheckConstraint, UniqueConstraint
from .base import Base, TimestampMixin
import uuid


class OrganizationMembership(Base, TimestampMixin):
    __tablename__ = "organization_memberships"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id", "organization_id", name="uq_organization_memberships_user_org"
        ),
        CheckConstraint(
            role.in_(["owner", "admin", "member", "viewer"]),
            name="organization_memberships_role_check",
        ),
    )
