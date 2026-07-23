import pytest
from petos_api.services.auth_service import AuthService
from petos_api.schemas.auth import RegisterRequest, LoginRequest
from petos_api.core.errors import AppError


@pytest.mark.asyncio
async def test_register_success(db_session):
    auth_service = AuthService(db_session)
    req = RegisterRequest(
        email="test@example.com",
        password="SuperSecretPassword123!",
        display_name="Test User",
    )
    user_res, token = await auth_service.register(req)

    assert user_res.email == "test@example.com"
    assert user_res.display_name == "Test User"
    assert token is not None


@pytest.mark.asyncio
async def test_register_duplicate(db_session):
    auth_service = AuthService(db_session)
    req = RegisterRequest(
        email="dup@example.com",
        password="SuperSecretPassword123!",
        display_name="Dup User",
    )
    await auth_service.register(req)

    with pytest.raises(AppError) as exc_info:
        await auth_service.register(req)

    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "email_in_use"


@pytest.mark.asyncio
async def test_login_success(db_session):
    auth_service = AuthService(db_session)
    req = RegisterRequest(
        email="login@example.com",
        password="SuperSecretPassword123!",
        display_name="Login User",
    )
    await auth_service.register(req)

    login_req = LoginRequest(
        email="login@example.com", password="SuperSecretPassword123!"
    )
    user_res, token = await auth_service.login(login_req)

    assert user_res.email == "login@example.com"
    assert token is not None


@pytest.mark.asyncio
async def test_login_invalid_password(db_session):
    auth_service = AuthService(db_session)
    req = RegisterRequest(
        email="login_invalid@example.com",
        password="SuperSecretPassword123!",
        display_name="Login Invalid User",
    )
    await auth_service.register(req)

    login_req = LoginRequest(email="login_invalid@example.com", password="wrong")

    with pytest.raises(AppError) as exc_info:
        await auth_service.login(login_req)

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "invalid_credentials"
