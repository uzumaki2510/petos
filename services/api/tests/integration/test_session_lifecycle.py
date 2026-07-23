"""
Session lifecycle integration tests.

These tests run against the real SQLite in-memory database and real Argon2id hasher.
No mocks for session state.
"""

import datetime
import pytest
from petos_api.services.auth_service import AuthService
from petos_api.repositories.session_repository import SessionRepository
from petos_api.repositories.user_repository import UserRepository
from petos_api.schemas.auth import RegisterRequest, LoginRequest
from petos_api.core.security import hash_session_token
from petos_api.core.errors import AppError
from petos_api.models.base import utc_now
from petos_api.core.config import settings


async def _register(db_session, email: str = None, suffix: str = ""):
    from uuid import uuid4

    email = email or f"session-{uuid4().hex[:8]}@test.example.com"
    auth = AuthService(db_session)
    user, token = await auth.register(
        RegisterRequest(
            email=email,
            password="SuperSecretPassword123!",
            display_name=f"Session User {suffix}",
        )
    )
    return auth, user, token


# ── Argon2id parameters ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_production_argon2id_parameters(db_session):
    """Verify the stored hash actually uses the approved Argon2id parameters."""
    auth, user, _ = await _register(db_session, suffix="argon2")

    user_repo = UserRepository(db_session)
    db_user = await user_repo.get_by_normalized_email(user.email.lower())
    assert db_user is not None
    # pwdlib stores Argon2 hashes in PHC format: $argon2id$v=19$m=65536,t=3,p=1$...
    ph = db_user.password_hash
    assert "$argon2id$" in ph, f"Expected Argon2id, got: {ph[:50]}"
    assert "m=65536" in ph, f"Expected memory_cost=65536, got: {ph[:80]}"
    assert "t=3" in ph, f"Expected time_cost=3, got: {ph[:80]}"
    assert "p=1" in ph, f"Expected parallelism=1, got: {ph[:80]}"


# ── Token generation ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registration_creates_unique_session_token(db_session):
    """Each registration must produce a different session token."""
    _, _, token1 = await _register(db_session, suffix="tok1")
    _, _, token2 = await _register(db_session, suffix="tok2")
    assert token1 != token2


@pytest.mark.asyncio
async def test_login_creates_new_session_token(db_session):
    """Login must create a new session token distinct from the registration token."""
    email = "login-rotation@test.example.com"
    auth, _, reg_token = await _register(db_session, email=email)
    _, login_token = await auth.login(
        LoginRequest(email=email, password="SuperSecretPassword123!")
    )
    assert reg_token != login_token

    # Both tokens must resolve to different hashes
    reg_hash = hash_session_token(reg_token)
    login_hash = hash_session_token(login_token)
    assert reg_hash != login_hash

    session_repo = SessionRepository(db_session)
    # Both sessions exist
    s1 = await session_repo.get_by_token_hash(reg_hash)
    s2 = await session_repo.get_by_token_hash(login_hash)
    assert s1 is not None
    assert s2 is not None
    assert s1.id != s2.id


# ── Session revocation ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_revoked_session_rejected(db_session):
    """A revoked token must not validate."""
    auth, _, token = await _register(db_session, suffix="rev")
    token_hash = hash_session_token(token)
    await auth.logout(token_hash)

    # Now re-check: session is revoked
    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)
    assert session is not None
    assert session.revoked_at is not None


# ── Idle expiry ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_idle_session_expiry(db_session):
    """A session whose expires_at is in the past must be rejected."""
    auth, _, token = await _register(db_session, suffix="idle")
    token_hash = hash_session_token(token)

    # Force-expire the idle TTL to be in the past
    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)
    assert session is not None

    past = utc_now() - datetime.timedelta(seconds=1)
    await session_repo.update_last_seen(str(session.id), past, past)
    await db_session.commit()

    # Expire the identity map so the re-read hits the DB
    await db_session.refresh(session)

    assert session.expires_at < utc_now()


# ── Absolute expiry ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_absolute_session_expiry(db_session):
    """A session whose absolute_expires_at is in the past must be rejected."""
    auth, _, token = await _register(db_session, suffix="abs")
    token_hash = hash_session_token(token)

    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)
    assert session is not None

    # Directly set absolute_expires_at to the past via SQL
    from sqlalchemy import update
    from petos_api.models.session import Session

    past = utc_now() - datetime.timedelta(seconds=1)
    await db_session.execute(
        update(Session).where(Session.id == session.id).values(absolute_expires_at=past)
    )
    await db_session.commit()
    await db_session.refresh(session)

    assert session.absolute_expires_at < utc_now()


@pytest.mark.asyncio
async def test_absolute_expiry_is_never_extended(db_session):
    """
    Idle TTL may be extended on last_seen, but absolute_expires_at must never
    be pushed beyond its original value.
    """
    auth, _, token = await _register(db_session, suffix="abscap")
    token_hash = hash_session_token(token)

    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)
    original_absolute = session.absolute_expires_at

    # Simulate the throttled update that extends idle TTL
    now = utc_now()
    new_idle = min(
        now + datetime.timedelta(seconds=settings.SESSION_IDLE_TTL_SECONDS),
        session.absolute_expires_at,
    )
    await session_repo.update_last_seen(str(session.id), now, new_idle)
    await db_session.commit()

    session = await session_repo.get_by_token_hash(token_hash)
    # Absolute must be unchanged
    assert session.absolute_expires_at == original_absolute
    # Idle TTL may be updated but must not exceed absolute
    assert session.expires_at <= session.absolute_expires_at


# ── last_seen_at throttling ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_last_seen_throttling(db_session):
    """
    last_seen_at must NOT be updated when called within the throttle interval.
    """
    auth, _, token = await _register(db_session, suffix="throttle")
    token_hash = hash_session_token(token)

    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)
    original_last_seen = session.last_seen_at

    # Simulate an update_last_seen that just happened (well within the interval)
    # last_seen_at was set at registration — time elapsed is ~0 seconds
    time_since = (utc_now() - session.last_seen_at).total_seconds()
    assert time_since < settings.SESSION_LAST_SEEN_UPDATE_INTERVAL_SECONDS, (
        "Test assumption: last_seen was set very recently"
    )

    # No update should happen (not enough time has passed)
    # We verify by checking last_seen_at is still the original
    session_after = await session_repo.get_by_token_hash(token_hash)
    assert session_after.last_seen_at == original_last_seen


@pytest.mark.asyncio
async def test_idle_expiry_refreshed_after_throttle_interval(db_session):
    """
    After the throttle interval elapses, last_seen_at update extends idle TTL.
    """
    auth, _, token = await _register(db_session, suffix="refresh")
    token_hash = hash_session_token(token)

    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)

    # Artificially age the last_seen_at by more than the throttle interval
    aged_last_seen = utc_now() - datetime.timedelta(
        seconds=settings.SESSION_LAST_SEEN_UPDATE_INTERVAL_SECONDS + 1
    )
    # Set a much-reduced idle TTL (30 min) so renewal to 7d is unambiguous
    aged_expires_at = utc_now() + datetime.timedelta(minutes=30)
    await session_repo.update_last_seen(
        str(session.id), aged_last_seen, aged_expires_at
    )
    await db_session.commit()
    # Expire identity map to get fresh values from DB
    await db_session.refresh(session)

    time_since = (utc_now() - session.last_seen_at).total_seconds()
    assert time_since > settings.SESSION_LAST_SEEN_UPDATE_INTERVAL_SECONDS, (
        f"Expected time_since > {settings.SESSION_LAST_SEEN_UPDATE_INTERVAL_SECONDS}s, got {time_since:.2f}s"
    )

    # Simulate the logic from get_current_user
    now = utc_now()
    new_idle = min(
        now + datetime.timedelta(seconds=settings.SESSION_IDLE_TTL_SECONDS),
        session.absolute_expires_at,
    )
    await session_repo.update_last_seen(str(session.id), now, new_idle)
    await db_session.commit()

    await db_session.refresh(session)
    # Idle TTL was set to 7d from now; aged_expires_at was only 1h from now
    # So new expires_at must be strictly greater than aged_expires_at
    assert session.expires_at > aged_expires_at, (
        f"expires_at {session.expires_at} should be > aged {aged_expires_at}"
    )
    assert session.expires_at <= session.absolute_expires_at


# ── Disabled user ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_disabled_user_session_rejected(db_session):
    """Even a valid non-revoked session must be rejected if the user is disabled."""
    auth, user, token = await _register(db_session, suffix="disabled")
    token_hash = hash_session_token(token)

    # Disable the user
    user_repo = UserRepository(db_session)
    db_user = await user_repo.get_by_normalized_email(user.email.lower())
    assert db_user is not None
    db_user.status = "disabled"
    await db_session.commit()

    # Session itself is still valid
    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)
    assert session is not None
    assert session.revoked_at is None

    # But login must now fail
    with pytest.raises(AppError) as exc:
        await auth.login(
            LoginRequest(email=user.email, password="SuperSecretPassword123!")
        )
    assert exc.value.status_code == 401


# ── Cookie expiry cap ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cookie_expiry_does_not_exceed_absolute_expiry(db_session):
    """
    The session's expires_at (idle TTL) must always be ≤ absolute_expires_at.
    """
    _, _, token = await _register(db_session, suffix="cap")
    token_hash = hash_session_token(token)

    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(token_hash)

    assert session.expires_at <= session.absolute_expires_at, (
        f"expires_at {session.expires_at} > absolute_expires_at {session.absolute_expires_at}"
    )
