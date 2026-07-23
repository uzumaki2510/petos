from typing import Tuple
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.models.user import User
from petos_api.models.session import Session
from petos_api.models.organization import Organization
from petos_api.models.organization_membership import OrganizationMembership
from petos_api.repositories.user_repository import UserRepository
from petos_api.repositories.session_repository import SessionRepository
from petos_api.repositories.organization_repository import OrganizationRepository
from petos_api.repositories.membership_repository import MembershipRepository
from petos_api.schemas.auth import RegisterRequest, LoginRequest
from petos_api.schemas.user import UserResponse
from petos_api.core.security import (
    hash_password,
    verify_password,
    generate_session_token,
    hash_session_token,
)
from petos_api.core.config import settings
from petos_api.core.errors import AppError
from petos_api.models.base import utc_now

import uuid
import re


class AuthService:
    def __init__(self, session: AsyncSession):
        self.db_session = session
        self.user_repo = UserRepository(session)
        self.session_repo = SessionRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.membership_repo = MembershipRepository(session)

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def _generate_org_slug(self, display_name: str) -> str:
        base_slug = re.sub(r"[^a-z0-9]+", "-", display_name.lower()).strip("-")
        if not base_slug:
            base_slug = "org"
        return f"{base_slug}-{uuid.uuid4().hex[:6]}"

    async def register(self, req: RegisterRequest) -> Tuple[UserResponse, str]:
        """
        Registers a new user and creates their personal organization.
        Returns the UserResponse and the cleartext session token.
        """
        normalized_email = self._normalize_email(req.email)

        # We must use a generic response for duplicates, but we still check
        existing_user = await self.user_repo.get_by_normalized_email(normalized_email)
        if existing_user:
            raise AppError(
                status_code=409, code="email_in_use", message="Registration conflict"
            )

        hashed_pwd = hash_password(req.password)

        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=req.email,
            normalized_email=normalized_email,
            password_hash=hashed_pwd,
            display_name=req.display_name,
            status="active",
        )
        self.user_repo.add(user)
        await self.db_session.flush()

        org_id = uuid.uuid4()
        org_slug = self._generate_org_slug(req.display_name)
        org = Organization(
            id=org_id,
            name=f"{req.display_name}'s Workspace",
            slug=org_slug,
            created_by=user_id,
        )
        self.org_repo.add(org)
        await self.db_session.flush()

        membership = OrganizationMembership(
            id=uuid.uuid4(), user_id=user_id, organization_id=org_id, role="owner"
        )
        self.membership_repo.add(membership)

        cleartext_token = generate_session_token()
        hashed_token = hash_session_token(cleartext_token)

        now = utc_now()
        idle_expires = now + datetime.timedelta(
            seconds=settings.SESSION_IDLE_TTL_SECONDS
        )
        absolute_expires = now + datetime.timedelta(
            seconds=settings.SESSION_ABSOLUTE_TTL_SECONDS
        )

        session = Session(
            id=uuid.uuid4(),
            token_hash=hashed_token,
            user_id=user_id,
            expires_at=idle_expires,
            absolute_expires_at=absolute_expires,
            last_seen_at=now,
        )
        self.session_repo.add(session)

        try:
            await self.db_session.commit()
            await self.db_session.refresh(user)
        except Exception:
            await self.db_session.rollback()
            # If unique constraint violation occurs concurrently, it throws here
            raise AppError(
                status_code=409, code="email_in_use", message="Registration conflict"
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ), cleartext_token

    async def login(self, req: LoginRequest) -> Tuple[UserResponse, str]:
        normalized_email = self._normalize_email(req.email)
        user = await self.user_repo.get_by_normalized_email(normalized_email)

        invalid_credentials_err = AppError(
            status_code=401,
            code="invalid_credentials",
            message="Unable to authenticate with the provided credentials.",
        )

        if not user or user.status == "disabled":
            # Optional: Hash a dummy password to prevent timing attacks, but Argon2 takes ~500ms
            # This is out of scope unless strictly required, but for safety:
            hash_password("dummy")
            raise invalid_credentials_err

        is_valid, new_hash = verify_password(req.password, user.password_hash)
        if not is_valid:
            raise invalid_credentials_err

        if new_hash:
            user.password_hash = new_hash
            # We don't commit immediately, we commit at the end with the session creation

        cleartext_token = generate_session_token()
        hashed_token = hash_session_token(cleartext_token)

        now = utc_now()
        idle_expires = now + datetime.timedelta(
            seconds=settings.SESSION_IDLE_TTL_SECONDS
        )
        absolute_expires = now + datetime.timedelta(
            seconds=settings.SESSION_ABSOLUTE_TTL_SECONDS
        )

        session = Session(
            id=uuid.uuid4(),
            token_hash=hashed_token,
            user_id=user.id,
            expires_at=idle_expires,
            absolute_expires_at=absolute_expires,
            last_seen_at=now,
        )
        self.session_repo.add(session)

        await self.db_session.commit()

        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ), cleartext_token

    async def logout(self, token_hash: str) -> None:
        now = utc_now()
        await self.session_repo.revoke_session(token_hash, now)
        await self.db_session.commit()
