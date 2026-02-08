# ha-semantic-memory — Codebase State

**Last Updated:** 2026-02-08
**Version:** 0.2.0
**Status:** Production — Stable

---

## Project Overview

FastAPI backend providing semantic memory for Home Assistant voice assistants. Uses PostgreSQL + pgvector for vector similarity search and pg_trgm for trigram matching. Embeddings generated via Ollama (nomic-embed-text, 768 dimensions).

**Architecture:**
```
HAOS (Pyscript thin client) → FastAPI :8920 → PostgreSQL + pgvector
                                             → Ollama embeddings
```

---

## Current State

- **26/26 tests passing** (unit, integration, auth, e2e, embeddings)
- **Production deployment**: macOS launchd service on Mac Mini
- **HAOS integration**: Pyscript client deployed, blueprint active
- **Consumers**: HA voice assistants (Marmaduke + Duke via Grok, GLM-4 fallback via Ollama), claude-memory-mcp

---

## Recent Major Work

- **Aggressive memory prompt (Duke)**: Second Grok conversation agent with silent, permission-free memorization. Documented in `docs/AGGRESSIVE_MEMORY_PROMPT.md`
- **Docs fix — operation vs action**: Fixed `docs/SYSTEM_PROMPT.md` to use `operation` (matching live HAOS deployment), documented repo/live divergence
- **Two-agent pattern**: Marmaduke (standard) + Duke (aggressive) — same backend, behavior controlled by system prompt
- **Per-user memory scoping**: All operations scoped by `user_id` via `(key, user_id)` unique constraint
- **Optional bearer token auth**: `HAMEM_API_TOKEN` env var, `/health` always bypasses

---

## Next Planned Work

- Test Duke agent more extensively across conversation types
- Memory expiration cleanup cron (especially for `event/` prefixed temporal items)
- Add `created_at`/`last_used_at` timestamps to MemoryItem API response
- Consider admin/list-all endpoint for cross-user memory inspection
- Decide whether to sync repo blueprint to `operation` or keep `action` as reference
- Bulk import/export endpoints
- Search analytics / usage metrics

---

## Testing Status

| Suite | Count | Status |
|-------|-------|--------|
| Unit (memory_service) | 7 | Pass |
| Integration (API) | 8 | Pass |
| Auth middleware | 3 | Pass |
| End-to-end | 5 | Pass |
| Embeddings | 3 | Pass |
| **Total** | **26** | **All passing** |

Run: `pytest tests/ -v`

---

## Key Files

| File | Purpose |
|------|---------|
| `server/main.py` | FastAPI app entry, lifespan, middleware |
| `server/config.py` | Pydantic settings (`HAMEM_` prefix) |
| `server/db.py` | asyncpg pool, schema, pgvector setup |
| `server/services/memory_service.py` | Core CRUD + hybrid search |
| `server/routers/memory.py` | `/memory/*` endpoints |
| `server/auth.py` | Optional bearer token middleware |
| `pyscript/ha_semantic_memory.py` | HAOS thin client (deploy via SSH) |
| `blueprints/ha_semantic_memory/memory_tool.yaml` | HA script blueprint (uses `action`; live HAOS uses `operation`) |
| `docs/AGGRESSIVE_MEMORY_PROMPT.md` | Duke agent's aggressive memorizer prompt |
