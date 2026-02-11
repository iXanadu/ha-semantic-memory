"""Integration tests for the HTTP API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert "checks" in data


@pytest.mark.asyncio
async def test_set_and_get(client):
    # Set
    resp = await client.post("/memory/set", json={
        "key": "test_api_key",
        "value": "test_api_value",
        "tags": "testing api",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Get
    resp = await client.post("/memory/get", json={"key": "test_api_key"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["memory"]["value"] == "test_api_value"

    # Clean up
    await client.post("/memory/forget", json={"key": "test_api_key"})


@pytest.mark.asyncio
async def test_search(client):
    # Store a memory
    await client.post("/memory/set", json={
        "key": "favorite_color",
        "value": "blue",
        "tags": "preference color",
    })

    # Search semantically
    resp = await client.post("/memory/search", json={
        "query": "what color do they like",
        "limit": 3,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert len(data["results"]) > 0
    assert any(r["key"] == "favorite_color" for r in data["results"])

    # Clean up
    await client.post("/memory/forget", json={"key": "favorite_color"})


@pytest.mark.asyncio
async def test_forget(client):
    await client.post("/memory/set", json={"key": "to_delete", "value": "gone"})
    resp = await client.post("/memory/forget", json={"key": "to_delete"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    resp = await client.post("/memory/get", json={"key": "to_delete"})
    assert resp.json()["status"] == "not_found"


@pytest.mark.asyncio
async def test_get_not_found(client):
    resp = await client.post("/memory/get", json={"key": "nonexistent_key_12345"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "not_found"


@pytest.mark.asyncio
async def test_search_empty_query_rejected(client):
    resp = await client.post("/memory/search", json={"query": ""})
    assert resp.status_code == 422

    resp = await client.post("/memory/search", json={"query": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_escalation_stub(client):
    resp = await client.post("/escalate")
    assert resp.status_code == 501
