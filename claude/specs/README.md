# Specifications

## Primary Documentation

- **`docs/SYSTEM_PROMPT.md`** — Recommended LLM system prompt for HA integration
- **`docs/MODEL_SELECTION.md`** — LLM model comparison for tool-calling reliability
- **`README.md`** — Full user documentation, architecture, setup guide, API reference

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/memory/set` | POST | Store/update a memory |
| `/memory/get` | POST | Retrieve by exact key |
| `/memory/search` | POST | Semantic + trigram hybrid search |
| `/memory/forget` | POST | Delete by key |
| `/health` | GET | Service health check |

## Search Algorithm

Hybrid scoring: `vec_score + (trigram_weight * trgm_score)`

- Vector: cosine similarity on 768-dim nomic-embed-text embeddings
- Trigram: pg_trgm similarity on concatenated search text
- Configurable thresholds via `HAMEM_VECTOR_THRESHOLD`, `HAMEM_TRIGRAM_WEIGHT`, `HAMEM_TRIGRAM_THRESHOLD`
