# Contributing to Folio

Thanks for your interest. Folio is pre-alpha; the API will churn.

## Dev setup

```bash
# Backend
cd backend
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest

# Frontend
cd frontend
pnpm install
pnpm dev
```

## Workflow

1. Open an issue describing the problem/feature before large PRs.
2. One logical change per PR; keep diffs reviewable.
3. Run `make lint test` before pushing.
4. Add or update evals when touching retrieval, chunking, or generation.
5. Sign commits with DCO (`git commit -s`).

## Scope guard

Folio is **not** trying to be LangChain. We stay opinionated:
- One default parser (Docling), one default embedder, one default store.
- Alternative providers live behind a stable interface, not scattered kwargs.
- No connector proliferation until core quality is proven on benchmarks.

If a PR adds surface area, it should also add an eval that proves the surface earns its keep.

## Reporting bugs

Use the issue template. Include: config YAML, model versions, corpus description, eval numbers if applicable.
