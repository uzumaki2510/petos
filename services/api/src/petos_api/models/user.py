from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CheckConstraint
from .base import Base, TimestampMixin
import uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    __table_args__ = (
        CheckConstraint(status.in_(["active", "disabled"]), name="users_status_check"),
    )
