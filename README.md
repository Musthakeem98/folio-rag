# Folio

> A local-first, open-source RAG system for PDFs, scans, and web content.

Folio gives you a self-hostable retrieval-augmented-generation stack that runs fully offline. Point it at a folder of PDFs or a list of URLs, ask questions, get answers with inline citations back to the source page/span.

## Why Folio

- **Local-first by default** — Ollama + local embeddings + embedded vector store. Zero API keys required.
- **PDF-grade retrieval** — Docling-based parsing (layout, tables, formulas), hybrid dense + BM25, cross-encoder reranking.
- **Eval-driven** — golden-set harness and public-benchmark runners in-tree, so quality claims are reproducible.
- **One-command self-host** — `docker compose up` brings up API, UI, Ollama, and vector store.
- **Opinionated defaults, pluggable internals** — swap parser, embedder, store, or LLM via config, not code forks.

## Quick start

```bash
# Clone and bring up the full stack
git clone <this-repo>.git folio && cd folio
cp .env.example .env
docker compose up -d

# Pull default models (Qwen2.5-7B + BGE-M3)
./scripts/pull-models.sh

# Open the UI
open http://localhost:3000
```

Or use the CLI directly against a local Python install — see [`backend/README.md`](backend/README.md).

## Architecture

```
                 ┌────────────────┐
                 │   Next.js UI   │  (chat, PDF viewer w/ highlights)
                 └────────┬───────┘
                          │ HTTP + SSE
                 ┌────────▼───────┐
                 │  FastAPI core  │
                 ├────────────────┤
   ingest ──────▶│ parser →       │
                 │ chunker →      │
                 │ embedder →     │──▶ LanceDB (vectors + metadata)
                 │ writer         │──▶ BM25 index (tantivy)
                 │                │
   query  ──────▶│ hybrid retr. →│
                 │ reranker →     │
                 │ context pack → │
                 │ LLM (Ollama)   │
                 └────────────────┘
```

See [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) for the full component map and [`docs/ROADMAP.md`](docs/ROADMAP.md) for phased milestones.

## Repository layout

```
backend/     FastAPI + ingest/retrieve/eval modules, Typer CLI
frontend/    Next.js 14 app (App Router) + chat + PDF citations UI
docker/      Container helpers (Ollama init, nginx reverse proxy)
configs/     Default YAML config, example overrides
scripts/     Bootstrap, model pulls, dev helpers
docs/        Blueprint, architecture, roadmap, eval methodology
```

## Status

Pre-alpha. Walking skeleton (Phase 1 of the roadmap). Not yet suitable for production.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
