"""
End-to-end tests: the critical semantic recall tests that motivated this project.
These require a running PostgreSQL and Ollama instance.
"""

import pytest
import pytest_asyncio

# Memories to store for testing
TEST_MEMORIES = [
    {"key": "my_location", "value": "Portland, OR", "tags": "home address city"},
    {"key": "wife_name", "value": "Sarah", "tags": "spouse family"},
    {"key": "favorite_food", "value": "sushi", "tags": "preference food"},
    {"key": "pet_name", "value": "Rex", "tags": "dog pet animal"},
    {"key": "work_title", "value": "Software Engineer", "tags": "job career"},
]


@pytest_asyncio.fixture
async def seeded_client(client):
    """Client with test memories pre-loaded."""
    for mem in TEST_MEMORIES:
        await client.post("/memory/set", json=mem)
    yield client
    for mem in TEST_MEMORIES:
        await client.post("/memory/forget", json={"key": mem["key"]})


@pytest.mark.asyncio
async def test_where_do_i_live(seeded_client):
    """THE critical test: 'where do I live' must find my_location."""
    resp = await seeded_client.post("/memory/search", json={
        "query": "where do I live",
        "limit": 3,
    })
    data = resp.json()
    assert data["status"] == "ok"
    keys = [r["key"] for r in data["results"]]
    assert "my_location" in keys, f"my_location not found in results: {keys}"


@pytest.mark.asyncio
async def test_what_is_my_wifes_name(seeded_client):
    """THE other critical test: 'what is my wife's name' must find wife_name."""
    resp = await seeded_client.post("/memory/search", json={
        "query": "what is my wife's name",
        "limit": 3,
    })
    data = resp.json()
    assert data["status"] == "ok"
    keys = [r["key"] for r in data["results"]]
    assert "wife_name" in keys, f"wife_name not found in results: {keys}"


@pytest.mark.asyncio
async def test_what_do_i_do_for_work(seeded_client):
    resp = await seeded_client.post("/memory/search", json={
        "query": "what do I do for work",
        "limit": 3,
    })
    data = resp.json()
    keys = [r["key"] for r in data["results"]]
    assert "work_title" in keys, f"work_title not found in results: {keys}"


@pytest.mark.asyncio
async def test_what_is_my_dogs_name(seeded_client):
    resp = await seeded_client.post("/memory/search", json={
        "query": "what is my dog's name",
        "limit": 3,
    })
    data = resp.json()
    keys = [r["key"] for r in data["results"]]
    assert "pet_name" in keys, f"pet_name not found in results: {keys}"


@pytest.mark.asyncio
async def test_exact_key_still_works(seeded_client):
    """Exact key lookup should still work perfectly."""
    resp = await seeded_client.post("/memory/get", json={"key": "my_location"})
    data = resp.json()
    assert data["status"] == "ok"
    assert data["memory"]["value"] == "Portland, OR"
