import httpx
import numpy as np

from server.config import settings

_client: httpx.AsyncClient | None = None


async def init_client() -> None:
    global _client
    _client = httpx.AsyncClient(base_url=settings.ollama_url, timeout=30.0)


async def close_client() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def embed(text: str) -> np.ndarray:
    """Get embedding vector for a text string. Returns 768-dim numpy array."""
    if _client is None:
        raise RuntimeError("Embedding client not initialized")
    resp = await _client.post(
        "/api/embed",
        json={"model": settings.embed_model, "input": text},
    )
    resp.raise_for_status()
    data = resp.json()
    return np.array(data["embeddings"][0], dtype=np.float32)


async def embed_batch(texts: list[str]) -> list[np.ndarray]:
    """Get embeddings for multiple texts in a single request."""
    if _client is None:
        raise RuntimeError("Embedding client not initialized")
    resp = await _client.post(
        "/api/embed",
        json={"model": settings.embed_model, "input": texts},
    )
    resp.raise_for_status()
    data = resp.json()
    return [np.array(v, dtype=np.float32) for v in data["embeddings"]]


async def check_health() -> bool:
    """Check if Ollama is reachable and the model is available."""
    if _client is None:
        return False
    try:
        resp = await _client.post(
            "/api/embed",
            json={"model": settings.embed_model, "input": "health check"},
            timeout=10.0,
        )
        return resp.status_code == 200
    except Exception:
        return False
