# Attribution

This project builds on the work of **luuquangvu**, whose
[Home Assistant Memory Tool](https://github.com/luuquangvu/tutorials) provided
the original Pyscript + SQLite implementation and the blueprint-based tool
pattern that exposes memory operations to LLM-powered voice assistants.

The original design proved that HA voice assistants could reliably store and
recall user memories via tool calling. This project replaces the SQLite + FTS5
backend with pgvector semantic search while preserving the same LLM-facing
interface — zero prompt changes required.

Key contributions from the original:
- Blueprint YAML structure with LLM prompt tuning inputs
- Service interface design (`memory_set`, `memory_get`, `memory_search`, `memory_forget`)
- Field naming conventions and validation patterns
- The insight that Pyscript + response_variable is the right HA integration pattern
