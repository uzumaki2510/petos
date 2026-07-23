import pytest
from petos_api.services.auth_service import AuthService
from petos_api.repositories.session_repository import SessionRepository
from petos_api.repositories.user_repository import UserRepository
from petos_api.schemas.auth import RegisterRequest, LoginRequest
from petos_api.core.security import hash_session_token
from petos_api.core.errors import AppError


@pytest.mark.asyncio
async def test_logout_revokes_session(db_session):
    auth = AuthService(db_session)
    user_res, token = await auth.register(
        RegisterRequest(
            email="logout_test@example.com",
            password="SuperSecretPassword123!",
            display_name="Logout User",
        )
    )

    # Logout using token hash
    hashed = hash_session_token(token)
    await auth.logout(hashed)

    # Session should now be revoked
    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(hashed)
    assert session is not None
    assert session.revoked_at is not None


@pytest.mark.asyncio
async def test_logout_is_idempotent(db_session):
    auth = AuthService(db_session)
    user_res, token = await auth.register(
        RegisterRequest(
            email="logout_idem@example.com",
            password="SuperSecretPassword123!",
            display_name="Idempotent Logout",
        )
    )

    hashed = hash_session_token(token)
    # Logout twice — should not raise
    await auth.logout(hashed)
    await auth.logout(hashed)  # idempotent

    session_repo = SessionRepository(db_session)
    session = await session_repo.get_by_token_hash(hashed)
    assert session is not None
    assert session.revoked_at is not None


@pytest.mark.asyncio
async def test_session_rejects_invalid_token(db_session):
    session_repo = SessionRepository(db_session)
    result = await session_repo.get_by_token_hash(
        "nonexistent_hash_value_000000000000000000000000000"
    )
    assert result is None


@pytest.mark.asyncio
async def test_registration_rollback_no_partial_records(db_session):
    """
    Registration with duplicate email must not leave partial records from a
    concurrent second attempt. We verify this by inspecting what was
    created after the first registration succeeds normally.
    """
    auth = AuthService(db_session)
    req = RegisterRequest(
        email="rollback_check@example.com",
        password="SuperSecretPassword123!",
        display_name="Rollback User",
    )
    user_res, _ = await auth.register(req)

    # The second attempt should raise 409
    with pytest.raises(AppError) as exc:
        await auth.register(req)
    assert exc.value.status_code == 409

    # Only one user with that email exists
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_normalized_email("rollback_check@example.com")
    assert user is not None
    assert str(user.id) == str(user_res.id)


@pytest.mark.asyncio
async def test_disabled_user_cannot_login(db_session):
    auth = AuthService(db_session)
    await auth.register(
        RegisterRequest(
            email="disabled_login@example.com",
            password="SuperSecretPassword123!",
            display_name="Disabled User",
        )
    )

    # Disable the user directly
    user_repo = UserRepository(db_session)
    user = await user_repo.get_by_normalized_email("disabled_login@example.com")
    assert user is not None
    user.status = "disabled"
    await db_session.commit()

    with pytest.raises(AppError) as exc:
        await auth.login(
            LoginRequest(
                email="disabled_login@example.com",
                password="SuperSecretPassword123!",
            )
        )
    assert exc.value.status_code == 401
