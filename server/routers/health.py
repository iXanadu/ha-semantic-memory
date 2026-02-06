from fastapi import APIRouter

from server.db import get_pool
from server.embeddings import check_health as check_ollama

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    checks = {"postgres": False, "ollama": False}

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        checks["postgres"] = True
    except Exception:
        pass

    checks["ollama"] = await check_ollama()

    ok = all(checks.values())
    return {"status": "ok" if ok else "degraded", "checks": checks}
