# ha-semantic-memory

Persistent semantic memory for Home Assistant voice assistants. Your assistant remembers what you tell it — and actually finds it later, even when you phrase things differently.

> **You:** "Remember that I live in Portland"
>
> *...days later...*
>
> **You:** "Where do I live?"
> **Assistant:** "You live in Portland, OR."

This works because ha-semantic-memory searches by **meaning**, not keywords. The query "where do I live" has zero words in common with the stored key `my_location`, but vector similarity understands they're asking the same thing.

## How It Works

A **FastAPI** service runs on your host machine alongside Ollama. When your voice assistant stores or recalls a memory, the request flows through a thin Pyscript client on HAOS to this service, which:

- Generates **768-dimensional embeddings** via Ollama (nomic-embed-text)
- Stores them in **PostgreSQL + pgvector** with an HNSW index
- Searches using **hybrid vector + trigram matching** — semantic similarity as the primary signal, with fuzzy text matching as a boost

The same `script.memory_tool` blueprint interface is preserved, so it's a drop-in backend replacement if you're already using a memory tool.

### Background

This project was inspired by [luuquangvu's memory tool](https://github.com/luuquangvu/tutorials), which pioneered persistent memory for HA voice assistants. We wanted stronger recall — their FTS5 full-text search requires exact word overlap between queries and stored text, which meant natural questions often couldn't find the right memory. We rebuilt the search backend with pgvector semantic search to match by meaning instead of keywords.

| Query | FTS5 (keyword) | pgvector (semantic) |
|-------|:--------------:|:-------------------:|
| "where do I live" → `my_location: Portland, OR` | MISS | **MATCH** (0.67) |
| "what is my wife's name" → `wife_name: Sarah` | MISS | **MATCH** (0.87) |
| "what do I do for work" → `work_title: Software Engineer` | MISS | **MATCH** (0.65) |

## Architecture

```
HAOS (VM or dedicated)               Host machine
┌──────────────────────┐             ┌────────────────────────────┐
│ Pyscript thin client │──aiohttp──> │ FastAPI :8920              │
│ (50 lines)           │             │ ├─ PostgreSQL + pgvector   │
│                      │             │ │  └─ HNSW index (768d)    │
│ Blueprint (unchanged)│             │ └─ Ollama embeddings       │
│ script.memory_tool   │             │    └─ nomic-embed-text     │
└──────────────────────┘             └────────────────────────────┘
```

1. User speaks to the HA voice assistant (e.g., "Remember that I live in Portland")
2. The LLM decides to call `script.memory_tool` with action=set
3. The blueprint routes to `pyscript.memory_set`, which HTTP POSTs to the FastAPI service
4. FastAPI generates an embedding via Ollama, stores it in PostgreSQL with pgvector
5. On recall ("Where do I live?"), the LLM calls action=search
6. FastAPI embeds the query, runs hybrid vector+trigram search, returns semantically matching results
7. The LLM reads the results and responds naturally

## Prerequisites

### Skill level

This project requires **command-line access** to your host machine. You'll work with git, Python virtual environments, Docker, and SSH. The HA-side configuration (creating scripts, exposing entities) is done through the web UI, but the backend setup is terminal-based.

If you're less comfortable at the command line, [Claude Code](https://docs.anthropic.com/en/docs/claude-code) can walk you through the setup step by step — paste the instructions and it will adapt them to your specific paths and environment.

### Hardware

The biggest hardware requirement is the **conversation LLM running in Ollama**. Reliable tool calling — especially *proactive* tool calling (the model deciding on its own to store a fact) — requires a capable model, and capable models require significant VRAM/unified memory.

| Config | Status | Notes |
|--------|--------|-------|
| **32GB RAM/unified memory** | Tested | GLM-4.7-Flash (18.3GB) + nomic-embed-text (0.5GB) + PostgreSQL + OS. This is what we developed and tested on. |
| **24GB RAM/unified memory** | Possible | Would require a smaller conversation model. Tool calling reliability is uncertain — untested. |
| **16GB or less** | Not viable | Not enough headroom for a conversation model that reliably calls tools, plus embeddings and PostgreSQL. |

**Tested environment:** Mac Mini M4, 32GB unified memory, 1TB SSD, macOS, with HAOS running in a UTM/QEMU VM.

### Software

- **Home Assistant OS** with [Pyscript](https://github.com/custom-components/pyscript) installed (via HACS)
- **Ollama** running on the host machine with a model that supports tool calling (see [LLM Model Selection](#llm-model-selection))
- **Docker** (recommended) or native PostgreSQL 17+ with pgvector
- **Python 3.12+** on the host machine (via [pyenv](https://github.com/pyenv/pyenv) + [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv))

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/iXanadu/ha-semantic-memory.git
cd ha-semantic-memory

# Create a pyenv virtualenv and install
pyenv virtualenv 3.12 ha-semantic-memory-3.12
pyenv local ha-semantic-memory-3.12
pip install -e ".[dev]"
```

Or use the install script, which handles virtualenv creation, dependency installation, and service setup:

```bash
./scripts/install.sh
```

### 2. Start PostgreSQL

Using Docker (recommended — one command, no manual SQL):

```bash
docker compose up -d
```

This starts PostgreSQL 17 with pgvector. The `vector` and `pg_trgm` extensions are created automatically by the FastAPI app on first startup — no manual SQL needed.

<details>
<summary>Native PostgreSQL (without Docker)</summary>

```bash
# macOS with Homebrew
brew install postgresql@17 pgvector
brew services start postgresql@17
/opt/homebrew/opt/postgresql@17/bin/createdb ha_memory

# Linux (Ubuntu/Debian)
sudo apt install postgresql-17 postgresql-17-pgvector
sudo -u postgres createdb ha_memory
```

If using native PostgreSQL, update `HAMEM_DB_USER` and `HAMEM_DB_PASSWORD` in your `.env` to match your system configuration.

</details>

### 3. Configure

```bash
cp .env.example .env
```

If using `docker compose`, the defaults work without edits. If using native PostgreSQL, edit `HAMEM_DB_USER` and `HAMEM_DB_PASSWORD` to match your setup.

### 4. Pull the embedding model

```bash
ollama pull nomic-embed-text
```

This is a small model (274MB) that runs alongside your conversation LLM.

### 5. Start the service

```bash
uvicorn server.main:app --host 0.0.0.0 --port 8920
```

Or use the service scripts (installs and starts as a background service):

```bash
./scripts/install.sh    # one-time setup
./scripts/start.sh      # start the service
```

### 6. Verify

```bash
# Health check (confirms DB + Ollama connectivity)
curl http://localhost:8920/health

# Store a test memory
curl -X POST http://localhost:8920/memory/set \
  -H "Content-Type: application/json" \
  -d '{"key": "test_location", "value": "Portland, OR", "tags": "home, address"}'

# Semantic search — the whole point
curl -X POST http://localhost:8920/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "where do I live"}'
# Should return test_location with a score > 0.5
```

## HA Integration

These steps wire ha-semantic-memory into your Home Assistant voice pipeline.

### a. Install Pyscript

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. In HACS, search for **Pyscript** and install it
3. Add the following to your `configuration.yaml` (via File Editor or SSH):
   ```yaml
   pyscript:
     allow_all_imports: true
     hass_is_global: true
   ```
4. Restart Home Assistant

### b. Deploy the Pyscript client

Copy `pyscript/ha_semantic_memory.py` to your HAOS config directory:

```bash
# Via SSH (if Advanced SSH & Web Terminal addon is installed):
cat pyscript/ha_semantic_memory.py | \
  ssh YOUR_HAOS_USER@YOUR_HAOS_IP 'sudo tee /config/pyscript/ha_semantic_memory.py > /dev/null'

# Or use the File Editor addon in HA to create the file manually
```

**Important:** Edit `BACKEND_URL` in the file to point to your host machine's LAN IP:
```python
BACKEND_URL = "http://192.168.1.100:8920"  # your host's LAN IP
```

Then reload Pyscript: **Developer Tools → Services → `pyscript.reload`**

### c. Install the blueprint

Copy the blueprint directory to HAOS:

```bash
# Create the blueprint directory on HAOS
ssh YOUR_HAOS_USER@YOUR_HAOS_IP 'sudo mkdir -p /config/blueprints/script/ha_semantic_memory'

# Copy the blueprint
cat blueprints/ha_semantic_memory/memory_tool.yaml | \
  ssh YOUR_HAOS_USER@YOUR_HAOS_IP 'sudo tee /config/blueprints/script/ha_semantic_memory/memory_tool.yaml > /dev/null'
```

### d. Create the script from the blueprint

1. In HA, go to **Settings → Automations & Scenes → Scripts**
2. Click **+ Add Script → Use a Blueprint**
3. Select **HA Semantic Memory Tool**
4. Save the script (it will be created as `script.memory_tool` or similar — note the entity ID)

### e. Expose the script to your voice assistant

1. Go to **Settings → Voice Assistants**
2. Select your Ollama-based assistant
3. Click the **Expose** tab (or go to **Settings → Voice Assistants → Expose Entities**)
4. Find your memory_tool script and toggle it **on**

### f. Configure the Ollama system prompt

Set the system prompt in **Settings → Devices & Services → Ollama → Configure**.

See [docs/SYSTEM_PROMPT.md](docs/SYSTEM_PROMPT.md) for the full recommended prompt with explanations of each section.

The key requirement: the prompt must instruct the LLM to **call the memory tool proactively** when the user shares personal facts, and to **search before answering** personal questions.

### g. Test it

In the HA Assist dialog or your voice assistant app:

> **You:** "Remember that I live in Portland"
> **Assistant:** *(should call memory_tool with action=set, then confirm)*

> **You:** "Where do I live?"
> **Assistant:** *(should call memory_tool with action=search, then answer "Portland")*

If the assistant says "I'll remember that" without making a tool call, see [LLM Model Selection](#llm-model-selection) — your model may not support proactive tool calling.

## Service Management

The `scripts/` directory provides cross-platform service management. On macOS, the service runs as a **LaunchDaemon** (starts at boot, no login required — ideal for headless servers):

```bash
./scripts/install.sh     # Create virtualenv, install deps, register service
./scripts/start.sh       # Start the service
./scripts/restart.sh     # Restart (e.g., after git pull)
./scripts/uninstall.sh   # Stop and remove the service definition
```

> **Note:** These scripts use `sudo` internally for service registration commands. You may be prompted for your password.

These scripts auto-detect macOS (launchd) vs Linux (systemd). The install script generates the appropriate service definition with correct paths for your pyenv virtualenv.

The service auto-starts on boot and auto-restarts on crash.

### Updating

```bash
git pull origin main
./scripts/restart.sh
```

## Configuration

All settings via environment variables with `HAMEM_` prefix (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `HAMEM_DB_HOST` | `localhost` | PostgreSQL host |
| `HAMEM_DB_PORT` | `5432` | PostgreSQL port |
| `HAMEM_DB_NAME` | `ha_memory` | Database name |
| `HAMEM_DB_USER` | `hamem` | Database user |
| `HAMEM_DB_PASSWORD` | `hamem` | Database password |
| `HAMEM_OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `HAMEM_EMBED_MODEL` | `nomic-embed-text` | Embedding model name |
| `HAMEM_PORT` | `8920` | Server listen port |
| `HAMEM_VECTOR_THRESHOLD` | `0.35` | Min cosine similarity for results |
| `HAMEM_TRIGRAM_WEIGHT` | `0.15` | Weight multiplier for trigram score |
| `HAMEM_TRIGRAM_THRESHOLD` | `0.1` | Min trigram similarity for results |

## Search Algorithm

### Hybrid Search

The service uses a two-signal search combining vector similarity and trigram matching:

```sql
WITH vector_results AS (
    SELECT *, 1 - (embedding <=> query_vec) AS vec_score,
              similarity(search_text, query_text) AS trgm_score
    FROM memories
    WHERE expires_at IS NULL OR expires_at > NOW()
    ORDER BY embedding <=> query_vec
    LIMIT limit * 3
)
SELECT *, vec_score + (0.15 * trgm_score) AS combined_score
FROM vector_results
WHERE vec_score >= 0.35 OR trgm_score >= 0.1
ORDER BY combined_score DESC
LIMIT limit
```

- **Vector similarity** (primary): HNSW index with cosine distance. "where do I live" and "my location Portland OR" produce nearby embeddings because nomic-embed-text understands semantic relationships.
- **Trigram boost** (secondary): `pg_trgm` catches exact substring matches and handles typos. Adds 15% weight.
- **OR fallback**: results surface if either signal is strong enough — you don't need both.

### Embedding Strategy

When storing a memory, the service builds a `search_text` field by combining:
- **Key expanded**: `my_location` → `my location` (snake_case to words)
- **Key raw**: `my_location`
- **Value**: `Portland, OR`
- **Tags**: `home, address`

Result: `"my location my_location Portland, OR home, address"`

This combined text gets embedded (768d vector via nomic-embed-text) AND stored for trigram indexing. The expansion ensures both the semantic meaning and exact key text are searchable.

## LLM Model Selection

**This matters more than you think.** Not all local LLMs reliably call tools — especially for *proactive* tool calling (storing facts without the user explicitly saying "remember").

We tested two models extensively:

| Capability | Qwen3-30B-A3B (Q4_K_S) | GLM-4.7-Flash (Q4_K_M) |
|-----------|:-----------------------:|:----------------------:|
| Explicit "remember X" | PASS | PASS |
| Proactive store ("I live in Portland") | **FAIL** | PASS |
| Recall ("Where do I live?") | **FAIL** | PASS |
| VRAM usage | 14.4 GB | 18.3 GB |

**Qwen3-30B-A3B** would respond with "Got it, I'll remember that!" but never actually call the tool — it generated text *about* calling the tool instead of making the tool call. This is a model-level limitation, not fixable through prompt engineering.

**GLM-4.7-Flash** reliably calls tools both proactively (detecting personal facts) and on recall (searching before answering). It passes all 6 pipeline tests.

See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for detailed findings and recommendations.

## Migration from SQLite

If you're migrating from the original luuquangvu SQLite-based memory tool:

```bash
# 1. Copy the SQLite database from HAOS to your host
ssh YOUR_HAOS_USER@YOUR_HAOS_IP 'sudo cat /config/memory.db' > memory.db

# 2. Run the migration (generates embeddings for all existing memories)
python migration/migrate_sqlite.py memory.db
```

The migration script reads all rows from the SQLite `mem` table, generates embeddings via Ollama, and inserts them into PostgreSQL. Existing keys are updated (upsert).

## Testing

```bash
pytest tests/ -v
```

27 tests covering:
- **Unit**: key expansion (`my_location` → `my location`), search text building
- **Embedding quality**: cosine similarity thresholds for semantic pairs (the critical validation)
- **API integration**: all CRUD endpoints (set, get, search, forget), input validation
- **Auth**: token enforcement, bypass for health endpoint
- **End-to-end**: store a memory, then retrieve it with a semantically different query

## Known Issues

### Tags Type Mismatch

Some LLMs send `tags` as a JSON array (`["family", "children"]`) instead of a comma-separated string (`"family, children"`). Both the FastAPI service and the Pyscript client normalize this automatically — arrays are joined with `", "` before processing. No action needed, but be aware if you see this in logs.

### Ollama Embedding Model Must Be Loaded

The nomic-embed-text model needs to be loaded in Ollama. If the service returns 500 errors, check:
```bash
curl -s http://localhost:11434/api/ps  # should show nomic-embed-text
ollama pull nomic-embed-text           # re-pull if missing
```

### Memory Expiration

Memories expire after 180 days by default (configurable per-memory via `expiration_days`). Set `expiration_days: 0` for permanent memories. Expired memories are excluded from search results but not automatically deleted from the database.

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | `/memory/set` | Store or update a memory |
| POST | `/memory/get` | Retrieve by exact key |
| POST | `/memory/search` | Semantic + trigram hybrid search |
| POST | `/memory/forget` | Delete by key |
| GET | `/health` | Service health (DB + Ollama check) |
| POST | `/escalate` | Cloud AI escalation (501 stub) |

## Project Structure

```
ha-semantic-memory/
├── server/
│   ├── main.py              # FastAPI app with lifespan
│   ├── config.py            # Pydantic Settings (.env)
│   ├── db.py                # asyncpg pool, schema, pgvector registration
│   ├── embeddings.py        # Ollama /api/embed client
│   ├── models.py            # Pydantic request/response models
│   ├── routers/
│   │   ├── memory.py        # /memory/* endpoints
│   │   ├── health.py        # /health
│   │   └── escalation.py    # /escalate (stub)
│   └── services/
│       └── memory_service.py # Core logic: CRUD + hybrid search
├── pyscript/
│   └── ha_semantic_memory.py # HAOS thin client (~50 lines)
├── blueprints/
│   └── ha_semantic_memory/
│       └── memory_tool.yaml  # HA Blueprint (backward-compatible)
├── scripts/
│   ├── install.sh            # Create virtualenv, deps, register service
│   ├── start.sh              # Start the service
│   ├── restart.sh            # Restart after updates
│   ├── uninstall.sh          # Stop and remove service definition
│   └── ollama-warmup.sh      # Pre-load Ollama models at boot
├── tests/                    # 27 pytest tests
├── migration/                # SQLite → pgvector migration script
├── docs/
│   ├── MODEL_SELECTION.md    # LLM model testing notes
│   └── SYSTEM_PROMPT.md      # Recommended Ollama system prompt
└── docker-compose.yml        # One-command PostgreSQL + pgvector
```

## License

MIT — see [LICENSE](LICENSE)

## Attribution

Inspired by the work of [luuquangvu](https://github.com/luuquangvu/tutorials), who brought persistent memory to HA voice assistants. See [ATTRIBUTION.md](ATTRIBUTION.md).
