# ha-semantic-memory — Context Memory

**Last Updated:** 2026-02-11
**Status:** Active — Production stable, service scripts deployed

---

## Current Focus

Production deployment hardened: service management scripts, LaunchDaemon for headless boot, proper pyenv virtualenv. Two-agent setup (Marmaduke + Duke) running. Next priorities: memory cleanup cron, API timestamp improvements.

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
| Two-agent pattern (Marmaduke + Duke) | Same backend, different prompts — behavior fully controlled by system prompt |
| `operation` is canonical field name | Live HAOS uses `operation`; repo blueprint's `action` diverged. Prompts must use `operation` |
| `recommended: false` for full Grok config | Grok integration hides model/temperature/max_tokens when `recommended: true` |
| LaunchDaemon over LaunchAgent | Mac Mini is headless — LaunchAgent requires login, LaunchDaemon starts at boot |
| Production in `/opt/srv/` | Separates production from dev (`~/projects/`), matches other services (AgentBeast, claude-memory-mcp) |
| Scripts handle sudo internally | Cleaner UX — user runs `./scripts/start.sh`, script calls `sudo launchctl` when needed |
| pyenv virtualenv (not .venv) | Consistent with project conventions, `.python-version` enables auto-activation |

---

## Environment

| Item | Value |
|------|-------|
| Python | 3.12.12 (pyenv virtualenv `ha-semantic-memory-3.12`) |
| Database | PostgreSQL 17, pgvector 0.8.1 |
| Embeddings | nomic-embed-text (768d) via Ollama |
| Port | 8920 |
| Config prefix | `HAMEM_` |
| Process manager | LaunchDaemon (macOS) |
| Production path | `/opt/srv/ha-semantic-memory` |
| Dev path | `~/projects/ha-semantic-memory` |

---

## Dependencies

- **Upstream**: Ollama (embeddings), PostgreSQL (storage)
- **Downstream**: claude-memory-mcp (MCP wrapper), HA voice assistant (via pyscript)

---

## Known Issues

- LLM may send `tags` as list instead of string — normalized in both pyscript and FastAPI
- Memory expiration is set per-record but no cleanup job runs yet
- Escalation endpoint (`/escalate`) returns 501 stub — superseded by direct Grok integration
- MemoryItem API response lacks `created_at`/`last_used_at` — can't determine memory age via API
- MCP and HA voice assistant use different `user_id` scoping — can't cross-query memories via MCP tools
- Repo blueprint uses `action` but live HAOS uses `operation` — diverged, needs decision on sync
- claude-memory-mcp has the same empty query bug (separate project, needs separate fix)

---

## HAOS Access

- SSH: `hassio@homeassistant` (key-based auth)
- HA long-lived token: `~/.config/ha-token`
- HA API: `http://homeassistant:8123/api/`
- HA user: Robert Pickles (`4c1e29b7ec324b1796de9bc5887319dc`)
- Grok entries: `01KGX31Z1PB5ANP6PTX80A0B04` (Marmaduke), `01KGXP4HTQJWXQXFEDSR5TG7Y0` (Duke)

## Notes

- The live blueprint on HAOS uses field name `operation` (not `action`) — system prompt must match
- Pyscript file in repo has a placeholder IP; must be substituted with real host IP when deploying to HAOS
- Grok HACS integration: `recommended: false` in config options exposes model, temperature, max_tokens fields
- Old LaunchDaemon (`com.macmini.ha-semantic-memory`) and wrapper script (`/usr/local/bin/ha-semantic-memory-start.sh`) have been removed
