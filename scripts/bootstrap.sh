#!/usr/bin/env bash
# One-shot local dev bootstrap: Python venv + Node deps.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

echo "==> backend venv"
if ! command -v uv >/dev/null 2>&1; then
  echo "install uv first:  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
(cd backend && uv venv && uv pip install -e ".[dev]")

echo "==> frontend deps"
if ! command -v pnpm >/dev/null 2>&1; then
  echo "install pnpm first:  corepack enable && corepack prepare pnpm@latest --activate"
  exit 1
fi
(cd frontend && pnpm install)

cp -n .env.example .env || true
echo "Bootstrap complete. Next: 'make up' (docker) or run backend + frontend separately."
