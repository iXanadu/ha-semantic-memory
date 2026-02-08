# ha-semantic-memory — Deployment Standards

## Architecture

This is a **local network service**, not a cloud/web application. No Nginx, no Gunicorn, no domain names.

```
Mac Mini (host)
├── FastAPI service (:8920) — launchd managed
├── PostgreSQL 17 — Homebrew / docker-compose
├── Ollama (:11434) — embeddings provider
└── HAOS VM (UTM/QEMU)
    └── Pyscript client → HTTP to host :8920
```

---

## Deployment Workflow

### Backend (FastAPI service)

1. Pull latest code: `git pull origin main`
2. Install any new dependencies: `pip install -e .`
3. Restart service: `launchctl kickstart -k gui/$(id -u)/com.ha-semantic-memory`
4. Verify: `curl http://localhost:8920/health`

No migrations needed — schema is auto-created on startup via `db.py`.

### Pyscript Client (HAOS)

Deployed separately to HAOS via SSH:

1. Update `pyscript/ha_semantic_memory.py` with the host's LAN IP (replace placeholder)
2. Upload to HAOS: `cat pyscript/ha_semantic_memory.py | ssh hassio@<HAOS_IP> 'sudo tee /config/pyscript/ha_semantic_memory.py > /dev/null'`
3. Reload pyscript: `curl -X POST -H "Authorization: Bearer <TOKEN>" http://<HAOS_IP>:8123/api/services/pyscript/reload`

### Blueprint

The blueprint in `blueprints/` is a reference copy. The live version on HAOS may have local modifications (e.g., `user_id` passthrough). Update carefully.

---

## Configuration

All configuration via environment variables with `HAMEM_` prefix. See `.env.example` for reference.

Key settings:
- `HAMEM_PORT` — server port (default: 8920)
- `HAMEM_DB_*` — PostgreSQL connection details
- `HAMEM_OLLAMA_URL` — Ollama endpoint
- `HAMEM_API_TOKEN` — optional bearer token (empty = disabled)

---

## Process Management

### macOS (launchd)

Plist: `launchd/com.ha-semantic-memory.plist`

```bash
# Start
launchctl load ~/Library/LaunchAgents/com.ha-semantic-memory.plist

# Restart
launchctl kickstart -k gui/$(id -u)/com.ha-semantic-memory

# Stop
launchctl unload ~/Library/LaunchAgents/com.ha-semantic-memory.plist

# Logs
tail -f /tmp/ha-semantic-memory.log
```

### Linux (systemd)

Unit file: `systemd/ha-semantic-memory.service`

```bash
sudo systemctl enable ha-semantic-memory
sudo systemctl start ha-semantic-memory
sudo systemctl status ha-semantic-memory
```

---

## Database

PostgreSQL with pgvector extension. Schema created automatically on first startup.

```bash
# Docker (quickstart)
docker-compose up -d

# Or manual
createdb ha_memory
psql ha_memory -c "CREATE EXTENSION vector; CREATE EXTENSION pg_trgm;"
```

---

## Health Check

```bash
curl http://localhost:8920/health
# Returns: {"status":"ok","checks":{"postgres":true,"ollama":true}}
```

`status` is `"degraded"` if either dependency is unreachable.
