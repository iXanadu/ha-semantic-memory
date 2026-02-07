"""Tests for optional bearer token authentication middleware."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch


@pytest_asyncio.fixture
async def authed_client(services):
    """Client for an app with HAMEM_API_TOKEN='test-secret'."""
    with patch("server.auth.settings") as mock_settings:
        mock_settings.api_token = "test-secret"
        from server.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


@pytest.mark.asyncio
async def test_no_token_configured_allows_all(client):
    """When HAMEM_API_TOKEN is empty, all requests pass through."""
    resp = await client.post("/memory/get", json={"key": "anything"})
    # Should get 200 (not_found), not 401
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_bypasses_auth(authed_client):
    """Health endpoint should always work, even with auth enabled."""
    resp = await authed_client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_missing_token_returns_401(authed_client):
    """Requests without a token should get 401."""
    resp = await authed_client.post("/memory/get", json={"key": "anything"})
    assert resp.status_code == 401
    assert "Authentication required" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_wrong_token_returns_401(authed_client):
    """Requests with the wrong token should get 401."""
    resp = await authed_client.post(
        "/memory/get",
        json={"key": "anything"},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert resp.status_code == 401
    assert "Invalid" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_correct_token_allows_request(authed_client):
    """Requests with the correct token should pass through."""
    resp = await authed_client.post(
        "/memory/get",
        json={"key": "anything"},
        headers={"Authorization": "Bearer test-secret"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "not_found"
