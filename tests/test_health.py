import pytest
from httpx import ASGITransport, AsyncClient

from app.admin.app import admin_app
from app.api.app import api_app


@pytest.fixture
async def api_client():
    async with AsyncClient(transport=ASGITransport(app=api_app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def admin_client():
    async with AsyncClient(transport=ASGITransport(app=admin_app), base_url="http://test") as c:
        yield c


async def test_api_health(api_client: AsyncClient):
    response = await api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_admin_health(admin_client: AsyncClient):
    response = await admin_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
