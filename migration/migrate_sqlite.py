#!/usr/bin/env python3
"""
Migrate memories from SQLite (HAOS) to PostgreSQL + pgvector.

Usage:
    python migration/migrate_sqlite.py path/to/memory.db

This reads all rows from the SQLite 'mem' table, generates embeddings
via Ollama, and inserts them into the PostgreSQL 'memories' table.
"""

import asyncio
import sqlite3
import sys
from pathlib import Path

import asyncpg
import httpx
import numpy as np


OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
PG_DSN = "postgresql://hamem:hamem@localhost:5432/ha_memory"


def expand_key(key: str) -> str:
    import re
    expanded = key.replace("_", " ").replace("-", " ")
    expanded = re.sub(r"([a-z])([A-Z])", r"\1 \2", expanded)
    return expanded.lower().strip()


def build_search_text(key: str, value: str, tags: str) -> str:
    key_expanded = expand_key(key)
    parts = [key_expanded, key, value]
    if tags:
        parts.append(tags)
    return " ".join(parts)


async def embed_text(client: httpx.AsyncClient, text: str) -> list[float]:
    resp = await client.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


async def migrate(sqlite_path: str):
    db = sqlite3.connect(sqlite_path)
    db.row_factory = sqlite3.Row
    rows = db.execute("SELECT * FROM mem").fetchall()
    db.close()

    print(f"Found {len(rows)} memories in SQLite")

    conn = await asyncpg.connect(PG_DSN)
    # Register pgvector
    from pgvector.asyncpg import register_vector
    await register_vector(conn)

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, row in enumerate(rows):
            key = row["key"]
            value = row["value"]
            scope = row.get("scope", "user") or "user"
            tags = row.get("tags", "") or ""
            tags_search = row.get("tags_search", "") or ""
            created_at = row.get("created_at", None)

            search_text = build_search_text(key, value, tags)
            embedding_list = await embed_text(client, search_text)
            embedding = np.array(embedding_list, dtype=np.float32)

            await conn.execute(
                """
                INSERT INTO memories (key, value, scope, tags, tags_search, embedding, search_text, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, COALESCE($8::timestamptz, NOW()))
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    scope = EXCLUDED.scope,
                    tags = EXCLUDED.tags,
                    tags_search = EXCLUDED.tags_search,
                    embedding = EXCLUDED.embedding,
                    search_text = EXCLUDED.search_text
                """,
                key, value, scope, tags, tags_search, embedding, search_text, created_at,
            )
            print(f"  [{i+1}/{len(rows)}] Migrated: {key}")

    await conn.close()
    print(f"\nMigration complete: {len(rows)} memories transferred")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-sqlite-db>")
        sys.exit(1)
    asyncio.run(migrate(sys.argv[1]))
