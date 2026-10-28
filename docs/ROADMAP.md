# Roadmap

Phased plan. Each phase ships something runnable so quality can be measured before adding the next layer.

## Phase 0 — Positioning (pre-code, done once)
- One-page README pitch, named differentiator.
- Benchmark pre-selection: FinanceBench + LegalBench-RAG as north-star corpora.

## Phase 1 — Walking skeleton (CURRENT)
- Scaffold: FastAPI, Typer CLI, Next.js UI, docker-compose.
- Protocols for parser / chunker / embedder / store / retriever / generator.
- Health endpoint reachable end-to-end through the compose stack.
- `pytest` + lint green.

## Phase 2 — Real ingest + retrieve
- Docling PDF parser wired, markdown-structural chunker wired.
- BGE-M3 embedder, LanceDB upsert path, dense retrieval returning real hits.
- BM25 index + RRF fusion.
- Cross-encoder reranker.
- `lumen index ./sample_docs` and `lumen ask "..."` produce cited answers from the CLI.

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
