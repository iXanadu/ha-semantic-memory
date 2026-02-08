# ha-semantic-memory

Semantic memory backend for Home Assistant voice assistants.
Replaces SQLite + FTS5 with FastAPI + pgvector + Ollama embeddings.

## Project Structure
- `server/` — FastAPI application (config, db, embeddings, routers, services)
- `pyscript/` — HA Pyscript thin client (~50 lines, async HTTP)
- `blueprints/` — HA Blueprint YAML (backward-compatible with original tool)
- `migration/` — SQLite → pgvector migration script
- `launchd/` — macOS auto-start plist
- `systemd/` — Linux systemd service file
- `tests/` — pytest suite (26 tests)
- `docs/` — System prompt guide, model selection notes

## Key Commands
- Run server: `uvicorn server.main:app --host 0.0.0.0 --port 8920`
- Run tests: `pytest tests/ -v`
- Check health: `curl http://localhost:8920/health`

## Conventions
- Config via env vars with `HAMEM_` prefix (see `server/config.py`)
- Port 8920
- PostgreSQL database: `ha_memory` (localhost, current user)
- Embedding model: nomic-embed-text via Ollama (:11434)
- All memory CRUD goes through `server/services/memory_service.py`
- Pyscript service names match original: `pyscript.memory_set/get/search/forget`
- Python environment: pyenv virtualenv (check `.python-version`)

## Critical Gotchas
- When deploying pyscript to HAOS, you MUST substitute the placeholder IP in `pyscript/ha_semantic_memory.py` with the actual host IP. The repo uses a placeholder; HAOS needs the real LAN IP.
- `@service` decorators MUST use `supports_response="optional"` — without it, HA 2024.10+ silently rejects calls from blueprints using `response_variable:`.
- LLM may send `tags` as a list instead of a string — both pyscript and FastAPI normalize this.
- The live blueprint on HAOS uses the field name `operation`, NOT `action` (the repo's reference blueprint uses `action`, but the live deployment diverged) — system prompts must use `operation` to match.

## Session State
- `claude/CODEBASE_STATE.md` — current technical state and recent work
- `claude/CONTEXT_MEMORY.md` — working context, decisions, priorities
- `claude/DEPLOYMENT_STANDARDS.md` — deployment and operations workflow
- `claude/session_progress/` — per-session work logs
