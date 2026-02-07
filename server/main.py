import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.auth import BearerTokenMiddleware
from server.config import settings
from server.db import close_pool, init_pool
from server.embeddings import close_client, init_client
from server.routers import escalation, health, memory

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ha-semantic-memory service")
    if settings.api_token:
        logger.info("API token authentication ENABLED")
    else:
        logger.info("API token authentication DISABLED (set HAMEM_API_TOKEN to enable)")
    await init_pool()
    await init_client()
    logger.info("Database pool and embedding client ready")
    yield
    logger.info("Shutting down")
    await close_client()
    await close_pool()


app = FastAPI(
    title="ha-semantic-memory",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(BearerTokenMiddleware)

app.include_router(memory.router)
app.include_router(health.router)
app.include_router(escalation.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )
