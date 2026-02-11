# ha-semantic-memory — Codebase State

**Last Updated:** 2026-02-11
**Version:** 0.2.1
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

- **27/27 tests passing** (unit, integration, auth, e2e, embeddings)
- **Production deployment**: macOS LaunchDaemon on Mac Mini (`/opt/srv/ha-semantic-memory`)
- **HAOS integration**: Pyscript client deployed, blueprint active
- **Consumers**: HA voice assistants (Marmaduke + Duke via Grok, GLM-4 fallback via Ollama), claude-memory-mcp
- **Service management**: `scripts/install.sh`, `start.sh`, `restart.sh`, `uninstall.sh`

---

## Recent Major Work

- **Empty query bug fix**: Empty/whitespace queries to `/memory/search` now return 422 instead of crashing (Pydantic validator + embed() guard)
- **Service management scripts**: Cross-platform install/start/restart/uninstall with auto-detect macOS (LaunchDaemon) vs Linux (systemd)
- **Production migration**: Moved from `~/projects/.venv` (LaunchAgent) to `/opt/srv/ha-semantic-memory` (LaunchDaemon) — starts at boot, no login required
- **pyenv virtualenv setup**: `ha-semantic-memory-3.12` with `.python-version`, replacing ad-hoc .venv
- **README overhaul**: All .venv references → pyenv, new service management docs, updated test count

---

## Next Planned Work

- Test Duke agent more extensively across conversation types
- Memory expiration cleanup cron (especially for `event/` prefixed temporal items)
- Add `created_at`/`last_used_at` timestamps to MemoryItem API response
- Consider admin/list-all endpoint for cross-user memory inspection
- Decide whether to sync repo blueprint to `operation` or keep `action` as reference
- Bulk import/export endpoints
- Search analytics / usage metrics
- Fix same empty query bug in claude-memory-mcp (separate project)

---

## Testing Status

| Suite | Count | Status |
|-------|-------|--------|
| Unit (memory_service) | 6 | Pass |
| Integration (API) | 7 | Pass |
| Auth middleware | 5 | Pass |
| End-to-end | 5 | Pass |
| Embeddings | 4 | Pass |
| **Total** | **27** | **All passing** |

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
| `server/models.py` | Pydantic request/response models (incl. empty query validation) |
| `scripts/install.sh` | Cross-platform service installation |
| `scripts/start.sh` | Start service + health check |
| `scripts/restart.sh` | Restart service + health check |
| `scripts/uninstall.sh` | Stop and remove service definition |
| `pyscript/ha_semantic_memory.py` | HAOS thin client (deploy via SSH) |
| `blueprints/ha_semantic_memory/memory_tool.yaml` | HA script blueprint (uses `action`; live HAOS uses `operation`) |
| `docs/AGGRESSIVE_MEMORY_PROMPT.md` | Duke agent's aggressive memorizer prompt |
