import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from petos_api.main import app
from petos_api.config import settings


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_live(client: AsyncClient):
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_ready_success(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    # Mock the database and redis checks to return True
    import petos_api.api.health

    monkeypatch.setattr(
        petos_api.api.health, "check_postgres", lambda: _async_return(True)
    )
    monkeypatch.setattr(
        petos_api.api.health, "check_redis", lambda: _async_return(True)
    )

    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["postgres"] == "ok"
    assert data["redis"] == "ok"
    assert data["version"] == settings.app_version


@pytest.mark.asyncio
async def test_health_ready_postgres_fail(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    import petos_api.api.health

    monkeypatch.setattr(
        petos_api.api.health, "check_postgres", lambda: _async_return(False)
    )
    monkeypatch.setattr(
        petos_api.api.health, "check_redis", lambda: _async_return(True)
    )

    response = await client.get("/health/ready")
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_health_ready_redis_fail(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    import petos_api.api.health

    monkeypatch.setattr(
        petos_api.api.health, "check_postgres", lambda: _async_return(True)
    )
    monkeypatch.setattr(
        petos_api.api.health, "check_redis", lambda: _async_return(False)
    )

    response = await client.get("/health/ready")
    assert response.status_code == 503


async def _async_return(val):
    return val
