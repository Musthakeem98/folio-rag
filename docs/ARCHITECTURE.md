# Architecture

Companion to [`BLUEPRINT.md`](BLUEPRINT.md) — this file goes deeper on the runtime wiring and data flows.

## Process model

A single FastAPI process hosts the API and the retrieval/generation pipeline. LanceDB is embedded (not a separate service). BM25 indices live on disk next to LanceDB tables. Heavy model-serving work — LLM inference and PDF parsing — runs in dedicated containers so the API image stays slim.

```
┌──────────────────────────────────────────────────────────┐
│ lumen-api (FastAPI, uvicorn)                             │
│                                                          │
│  /ingest ──▶ IngestPipeline ─▶ Chunker ─▶ Embedder ─┐    │
│                 │                                   │    │
│                 ▼ HTTP (parse)                      ▼    │
│                                           LanceDB (embed)│
│  /chat ──▶ QueryPipeline ─▶ Hybrid ─▶ Rerank ─▶ Ollama   │
│                                              ▲ HTTP      │
│                                              │           │
│           bm25s index (on disk)              │           │
└──────────────────────────────────────────────┼───────────┘
                      │                       │
                      ▼                       ▼
         ┌─────────────────────┐   ┌────────────────────────┐
         │ docling (:5001)     │   │ ollama (:11434)        │
         │ layout + OCR models │   │ Qwen2.5-7B / etc.      │
         └─────────────────────┘   └────────────────────────┘
```

## Why embedded vector store

- Zero ops: no second service to run, back up, or auth.
- Faster: no network hop on retrieval.
- Simpler release surface: one container holds all retrieval state.

The trade-off is that scaling-out requires swapping LanceDB for a networked store — which is why `VectorStore` is a Protocol with a Qdrant implementation planned.

## Ingest concurrency

Document parsing is delegated to the `docling` container over HTTP. The API fans out parse requests via a bounded `asyncio` pool; docling-serve handles its own internal concurrency (and GPU batching when the GPU profile is enabled). Embedding uses the model's native batch dim. Writes to LanceDB are batched (default 256 chunks per upsert).

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
