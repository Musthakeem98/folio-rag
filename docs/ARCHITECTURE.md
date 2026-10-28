# Architecture

Companion to [`BLUEPRINT.md`](BLUEPRINT.md) — this file goes deeper on the runtime wiring and data flows.

## Process model

A single FastAPI process hosts the API and all pipeline components. LanceDB is embedded (not a separate service). BM25 indices live on disk next to LanceDB tables.

```
┌──────────────────────────────────────────────────────────┐
│ lumen-api (FastAPI, uvicorn)                             │
│                                                          │
│  Routes ─▶ QueryPipeline ─▶ Hybrid ─▶ Rerank ─▶ Ollama   │
│                 │                                        │
│                 ▼                                        │
│           LanceDB (embedded)                             │
│           bm25s index (on disk)                          │
└──────────────────────────────────────────────────────────┘
                      │
                      │ HTTP (localhost)
                      ▼
┌──────────────────────────────────────────────────────────┐
│ ollama (separate container, exposes 11434)               │
└──────────────────────────────────────────────────────────┘
```

## Why embedded vector store

- Zero ops: no second service to run, back up, or auth.
- Faster: no network hop on retrieval.
- Simpler release surface: one container holds all retrieval state.

The trade-off is that scaling-out requires swapping LanceDB for a networked store — which is why `VectorStore` is a Protocol with a Qdrant implementation planned.

## Ingest concurrency

Document parsing is CPU-bound (Docling layout analysis). We fan out across a bounded `asyncio` worker pool whose size matches CPU count minus one. Embedding uses the model's native batch dim. Writes to LanceDB are batched (default 256 chunks per upsert).

## Query lifecycle

1. **Receive** — `/api/v1/chat/completions` with `{query, k, stream}`.
2. **Embed query** — one call to Embedder (BGE-M3).
3. **Fan out** — DenseRetriever and SparseRetriever in parallel.
4. **Fuse** — RRF over the two ranked lists.
5. **Rerank** — cross-encoder scores the top ~50; keep top k.
6. **Context pack** — reorder (relevance to middle avoided), dedupe near-duplicates, enforce token budget.
7. **Generate** — Ollama stream; tokens relayed as SSE `token` events.
8. **Finalize** — emit `done` SSE event with the final citation list.

## Error handling

- Transient Ollama / HF errors wrapped with `tenacity` retries (bounded, no infinite loops).
- Parser failures per-document do not fail the batch; the failed doc is recorded in the run report.
- All structured logs via `structlog` with request IDs.

## Testing strategy

- **Unit:** metrics, chunker boundaries, RRF fusion, protocol conformance.
- **Integration:** real LanceDB + real bm25s with tiny fixture corpora; mocked Ollama.
- **Eval:** the golden-set runner *is* the quality test; it runs in CI nightly and on PR label.
