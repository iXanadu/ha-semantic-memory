"""
Pyscript thin client for ha-semantic-memory.
Runs inside HAOS Pyscript integration. Calls the FastAPI service over HTTP.
Service names match the original luuquangvu tool for backward compatibility.

The blueprint calls these exact signatures — do not change parameter names.
Uses aiohttp from HA Core (pyscript is async-native, no task.executor needed).
"""

import json

from homeassistant.helpers.aiohttp_client import async_get_clientsession

# Set this to the LAN IP of the machine running ha-semantic-memory
# (must be reachable from HAOS — e.g., your host machine's IP on the same subnet)
BACKEND_URL = "http://YOUR_HOST_IP:8920"


async def _post(endpoint, payload):
    """Async HTTP POST using HA's shared aiohttp session."""
    session = async_get_clientsession(hass)
    async with session.post(
        f"{BACKEND_URL}/memory/{endpoint}",
        json=payload,
        timeout=10,
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


@service(supports_response="optional")
async def memory_set(key=None, value=None, scope="user", user_id="default", expiration_days=180, tags="", force_new="false"):
    """Store a memory."""
    # LLM may send tags as list — normalize to comma-separated string
    if isinstance(tags, list):
        tags = ", ".join(str(t) for t in tags)
    payload = {
        "key": key,
        "value": value,
        "scope": scope,
        "user_id": str(user_id) if user_id else "default",
        "tags": str(tags) if tags else "",
        "expiration_days": int(expiration_days) if expiration_days else 180,
        "force_new": str(force_new).lower() == "true",
    }
    try:
        result = await _post("set", payload)
        log.info(f"memory_set OK: key={key} user_id={user_id}")
        return result
    except Exception as e:
        log.error(f"memory_set FAILED: {e}")
        return {"status": "error", "message": str(e)}


@service(supports_response="optional")
async def memory_get(key=None, user_id="default"):
    """Retrieve a memory by key."""
    try:
        result = await _post("get", {"key": key, "user_id": str(user_id) if user_id else "default"})
        return result
    except Exception as e:
        log.error(f"memory_get FAILED: {e}")
        return {"status": "error", "message": str(e)}


@service(supports_response="optional")
async def memory_search(query=None, scope="user", user_id="default", limit=5):
    """Search memories semantically."""
    try:
        result = await _post("search", {
            "query": query,
            "scope": scope,
            "user_id": str(user_id) if user_id else "default",
            "limit": int(limit),
        })
        return result
    except Exception as e:
        log.error(f"memory_search FAILED: {e}")
        return {"status": "error", "message": str(e)}


@service(supports_response="optional")
async def memory_forget(key=None, user_id="default"):
    """Delete a memory."""
    try:
        result = await _post("forget", {"key": key, "user_id": str(user_id) if user_id else "default"})
        return result
    except Exception as e:
        log.error(f"memory_forget FAILED: {e}")
        return {"status": "error", "message": str(e)}
