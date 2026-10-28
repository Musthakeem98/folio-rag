# Roadmap

Phased plan. Each phase ships something runnable so quality can be measured before adding the next layer.

## Phase 0 — Positioning (pre-code, done once)
- One-page README pitch, named differentiator.
- Benchmark pre-selection: FinanceBench + LegalBench-RAG as north-star corpora.

## Phase 1 — Walking skeleton (DONE)
- Scaffold: FastAPI, Typer CLI, Next.js UI, docker-compose.
- Protocols for parser / chunker / embedder / store / retriever / generator.
- Health endpoint reachable end-to-end through the compose stack.
- `pytest` + lint green.

## Phase 2 — Real ingest (DONE for ingest, retrieve still pending)
- [x] Markdown-structural chunker (heading-aware, preserves tables and code).
- [x] Docling parser as a thin HTTP client to `docling-serve`.
- [x] Web parser via `trafilatura`.
- [x] BGE-M3 embedder (sentence-transformers, lazy-loaded, async-safe).
- [x] LanceDB vector store with upsert-by-doc-id semantics.
- [x] BM25 (`bm25s`) sparse index with on-disk persistence, rebuilt per ingest.
- [x] `IngestPipeline` factory wiring + `/api/v1/documents/{upload,url}` routes.
- [x] `lumen index <file|dir|url>` CLI.
- [x] Integration test: real LanceDB + BM25 against fixture corpus.
- [ ] Dense retrieval returning real hits (query path).
- [ ] Hybrid RRF fusion.
- [ ] Cross-encoder reranker.
- [ ] `lumen ask "..."` producing cited answers.

### Known gaps carried forward
- PDF page tracking: Docling exposes per-element provenance in its structured
  output; we currently take only markdown, so `Chunk.page` is `None` for PDFs.
  Fix by requesting the `doc` format and building a `char_offset → page` map.
- Ingest is inline on the upload endpoint. For large PDFs we want a background
  job queue (ARQ or Redis streams) and a `/jobs/{id}` status endpoint.
- BM25 is rebuilt from scratch after each ingest. Fine for personal corpora,
  but we'll want shard+append once a user has >100k chunks.

## Phase 3 — Eval harness
- Golden-set loader + runner.
- Recall@k, nDCG, faithfulness, citation precision metrics.
- CI runs the eval on PR; results posted as a PR comment.
- README publishes current scores on FinanceBench + LegalBench-RAG.

## Phase 4 — UI polish
- Streaming chat with inline citation chips.
- PDF viewer pane with highlight-on-citation-click.
- Document management (upload, list, delete, reindex).
- Dark mode, keyboard-driven navigation.

## Phase 5 — Launch
- OSS license, DCO, CONTRIBUTING polished.
- Hosted demo on HF Spaces or Fly.io.
- Launch posts: HN Show, r/LocalLLaMA, r/MachineLearning, X.
- Benchmark results teaser 2 weeks prior.

## Phase 6 — Beyond v1
Pick two, no more:
- GraphRAG via Kuzu for multi-hop.
- ColPali visual retrieval for figure-heavy PDFs.
- Agentic retrieval loop (query planning + self-correction).
- Incremental re-index with content-hash diffing.
- Qdrant backend for the first users who outgrow embedded storage.
