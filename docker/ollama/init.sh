#!/usr/bin/env sh
# Optional entrypoint wrapper for the ollama container that pulls default
# models on first start. Not used by default compose — see scripts/pull-models.sh.
set -e
ollama serve &
PID=$!
sleep 3
ollama pull "${LUMEN_LLM_MODEL:-qwen2.5:7b-instruct}" || true
wait "$PID"
