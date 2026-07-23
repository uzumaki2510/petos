import pytest
from httpx import AsyncClient, ASGITransport
from petos_api.main import app
import os


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_postgres_redis():
    """
    This test runs against the real local Postgres and Redis containers to verify End-to-End connectivity.
    It expects the development containers to be running.
    """
    if os.environ.get("ENVIRONMENT") != "development":
        pytest.skip("Skipping integration test outside of development environment")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok", (
            f"Integration test failed: DB or Redis not available: {data}"
        )
