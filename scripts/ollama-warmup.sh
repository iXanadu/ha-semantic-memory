#!/bin/bash
# Keep Ollama models warm — runs at boot and periodically via launchd
# GLM-4.7-Flash: conversation LLM (18GB, slow to cold-load)
# nomic-embed-text: embedding model for ha-semantic-memory

LOG="/tmp/ollama-warmup.log"

echo "$(date): Warming up models..." >> "$LOG"

# Wait for Ollama to be ready (important on boot)
for i in $(seq 1 30); do
    curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && break
    sleep 2
done

# Warm up GLM-4.7-Flash (keep_alive=-1 means it stays loaded forever after this)
curl -s http://localhost:11434/api/generate \
  -d '{"model":"glm-4.7-flash","prompt":"hi","stream":false,"options":{"num_predict":1}}' \
  > /dev/null 2>&1
echo "$(date): GLM-4.7-Flash loaded" >> "$LOG"

# Warm up nomic-embed-text with keep_alive to prevent unloading
curl -s http://localhost:11434/api/embed \
  -d '{"model":"nomic-embed-text","input":"warmup","keep_alive":"24h"}' \
  > /dev/null 2>&1
echo "$(date): nomic-embed-text loaded (24h keep_alive)" >> "$LOG"
