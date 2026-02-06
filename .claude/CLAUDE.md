# ha-semantic-memory

Semantic memory backend for the Marmaduke Home Assistant voice assistant.
Replaces SQLite + FTS5 with FastAPI + pgvector + Ollama embeddings.

## Project Structure
- `server/` — FastAPI application (config, db, embeddings, routers, services)
- `pyscript/` — HA Pyscript thin client (~50 lines, sync HTTP)
- `blueprints/` — HA Blueprint YAML (backward-compatible with original tool)
- `migration/` — SQLite → pgvector migration script
- `launchd/` — macOS auto-start plist
- `tests/` — pytest suite
- `docs/` — SPEC.md (living spec), architecture.md, migration.md

## Key Commands
- Run server: `cd ~/projects/ha-semantic-memory && .venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8920`
- Run tests: `cd ~/projects/ha-semantic-memory && .venv/bin/pytest tests/ -v`
- Check health: `curl http://localhost:8920/health`

## Conventions
- Config via env vars with `HAMEM_` prefix (see server/config.py)
- Port 8920
- PostgreSQL database: ha_memory (localhost, current user)
- Embedding model: nomic-embed-text via Ollama (:11434)
- All memory CRUD goes through memory_service.py
- Pyscript service names match original: pyscript.memory_set/get/search/forget
