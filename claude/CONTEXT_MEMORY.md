# ha-semantic-memory — Context Memory

**Last Updated:** 2026-02-07
**Status:** Stable / Maintenance

---

## Current Focus

Project is stable and in production. No active development. Available for bug fixes and enhancements as needed.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| pgvector over SQLite+FTS5 | Proper vector similarity search, better scaling, hybrid search capability |
| Hybrid vector + trigram search | Handles both semantic meaning and typo/keyword matching |
| Per-user scoping via `user_id` | HA supports multiple users; memories must be isolated |
| Optional bearer token auth | Security layer for network-exposed deployments without forcing it on local-only setups |
| Pyscript thin client pattern | Keeps HA-side code minimal; all logic in FastAPI backend |
| `supports_response="optional"` on services | Required for HA 2024.10+ when blueprint uses `response_variable:` |

---

## Environment

| Item | Value |
|------|-------|
| Python | 3.12 (pyenv virtualenv) |
| Database | PostgreSQL 17, pgvector 0.8.1 |
| Embeddings | nomic-embed-text (768d) via Ollama |
| Port | 8920 |
| Config prefix | `HAMEM_` |
| Process manager | launchd (macOS) |

---

## Dependencies

- **Upstream**: Ollama (embeddings), PostgreSQL (storage)
- **Downstream**: claude-memory-mcp (MCP wrapper), HA voice assistant (via pyscript)

---

## Known Issues

- LLM may send `tags` as list instead of string — normalized in both pyscript and FastAPI
- Memory expiration is set per-record but no cleanup job runs yet
- Escalation endpoint (`/escalate`) returns 501 stub — superseded by direct Grok integration

---

## Notes

- The live blueprint on HAOS uses field name `operation` (not `action`) — system prompt must match
- Pyscript file in repo has a placeholder IP; must be substituted with real host IP when deploying to HAOS
