import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from server.db import init_pool, close_pool
from server.embeddings import init_client, close_client


@pytest_asyncio.fixture(scope="session")
async def services():
    """Initialize DB pool and embedding client once for the entire test session."""
    await init_pool()
    await init_client()
    yield
    await close_client()
    await close_pool()


@pytest_asyncio.fixture
async def client(services):
    """Async HTTP client wired to the FastAPI app (with services initialized)."""
    from server.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
