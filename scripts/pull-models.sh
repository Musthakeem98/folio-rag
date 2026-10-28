#!/usr/bin/env bash
# Pull default Ollama models into the running ollama container.
set -euo pipefail

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
MODELS=("${LUMEN_LLM_MODEL:-qwen2.5:7b-instruct}")

for m in "${MODELS[@]}"; do
  echo "==> pulling $m"
  curl -fsSL -X POST "$OLLAMA_HOST/api/pull" -d "{\"name\":\"$m\"}" | tail -n 20
done

echo "Done. Embedding + reranker models (BGE-M3, bge-reranker-v2-m3) will be downloaded by the API on first use."
