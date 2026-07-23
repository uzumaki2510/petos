"""
BFF Gateway integration tests.

Tests that FastAPI's BFFGatewayMiddleware correctly rejects requests missing
or with an invalid BFF secret, while allowing requests with the correct secret.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from petos_api.main import app
from petos_api.core.config import settings


@pytest.fixture
def correct_secret():
    return settings.BFF_INTERNAL_SECRET


@pytest.fixture
def headers_with_secret(correct_secret):
    return {
        "X-PetOS-BFF-Secret": correct_secret,
        "X-PetOS-Client-IP": "127.0.0.1",
        "Content-Type": "application/json",
    }


@pytest.mark.asyncio
async def test_health_live_accessible_without_bff_secret():
    """Health endpoints must bypass the BFF gateway."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/live")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_ready_accessible_without_bff_secret():
    """Health/ready must bypass the BFF gateway."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")
    # 200 or 503 depending on DB/Redis state — must NOT be 403
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_protected_route_rejected_without_bff_secret():
    """Business endpoint without BFF secret must return 403."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/v1/auth/me")
    assert response.status_code == 403
    body = response.json()
    assert body.get("code") == "missing_bff_secret"


@pytest.mark.asyncio
async def test_protected_route_rejected_with_invalid_bff_secret():
    """Business endpoint with wrong BFF secret must return 403."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/v1/auth/me",
            headers={"X-PetOS-BFF-Secret": "completely-wrong-secret"},
        )
    assert response.status_code == 403
    body = response.json()
    assert body.get("code") == "invalid_bff_secret"


@pytest.mark.asyncio
async def test_protected_route_accepted_with_correct_bff_secret(headers_with_secret):
    """
    Business endpoint with correct BFF secret is passed through (may return 401
    for missing session, but must NOT be 403 from the gateway).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/v1/auth/me", headers=headers_with_secret)
    # 401 = gateway passed, no session. 403 = gateway blocked (wrong secret).
    assert response.status_code == 401, (
        f"Expected 401 (no session), got {response.status_code}: {response.text}"
    )


@pytest.mark.asyncio
async def test_login_rejected_without_bff_secret():
    """POST /v1/auth/login must be rejected by the gateway without BFF secret."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/auth/login",
            json={"email": "test@example.com", "password": "Test123!"},
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_rejected_without_bff_secret():
    """POST /v1/auth/register must be rejected by the gateway without BFF secret."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "display_name": "Test",
            },
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_empty_bff_secret_header_rejected():
    """An empty X-PetOS-BFF-Secret must be rejected."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/v1/auth/me",
            headers={"X-PetOS-BFF-Secret": ""},
        )
    assert response.status_code == 403
