# Lumen — Project Blueprint

> Working blueprint for a local-first, open-source RAG system. Lives in-repo so design decisions and their rationale are versioned with the code.

## 1. Thesis

The OSS RAG space is crowded but shallow. Most frameworks optimize for *coverage* (every parser × every store × every LLM) and under-deliver on *quality* (retrieval precision on real PDFs). Lumen inverts that: one opinionated path, measured obsessively, that beats the field on PDF-grade retrieval while running fully offline.

**One-line pitch:** `docker compose up` → point at a folder of PDFs → ask questions with cited answers, offline, with eval numbers you can reproduce.

## 2. Non-goals

- Hosted/SaaS offering. Lumen is self-hosted software.
- Agent framework. We don't orchestrate tools or multi-step workflows.
- Fine-tuning platform. Bring your own fine-tuned embedder; we expose the interface.
- Connector sprawl (Slack, Notion, Drive, Confluence, ...). Filesystem + URL only until core quality is proven.

## 3. Architecture

### 3.1 Services

| Service | Role | Default |
|---|---|---|
| **api** | FastAPI + ingest/retrieve/generate pipelines | Python 3.12 |
| **web** | Next.js 14 App Router UI | Node 20 |
| **ollama** | Local LLM runtime | Ollama latest |
| **docling** | PDF parsing (layout, tables, OCR) via docling-serve | docling-serve-cpu (gpu profile available) |
| *(optional)* **nginx** | Single-port reverse proxy for public exposure | nginx:alpine |

Everything runs in Docker Compose. The vector store (LanceDB) is embedded inside the API process — no separate DB container by default, no network hop, no auth plumbing. Docling runs separately so its ~GB of layout and OCR models stay out of the API image and GPU can be scoped to parsing only.

### 3.2 Pipelines

**Ingest** (file or URL → persisted chunks + vectors + BM25 index):

```
source → Parser → ParsedDoc(markdown) → Chunker → [Chunk]
      → Embedder → [vector] → VectorStore.upsert
                           → SparseIndex.fit (incremental)
```

**Query** (user question → cited answer):

```
query → DenseRetriever ─┐
                        ├─▶ HybridFuser (RRF) → Reranker → ContextPacker → Generator → Answer+Citations
      → SparseRetriever ┘
```

### 3.3 Component contracts

Each subpackage exposes a `base.py` with a Python `Protocol` or ABC. Implementations are swapped by config, not conditional imports in call sites.

- `ingest/parsers/base.py` — `Parser` protocol
- `ingest/chunker.py` — `Chunker` protocol
- `embed/base.py` — `Embedder` protocol
- `store/base.py` — `VectorStore` protocol
- `retrieve/{dense,bm25,hybrid,rerank}.py` — composable retrievers
- `generate/base.py` — `Generator` protocol (completion + streaming)

Factories in `core/pipeline.py` read the YAML config and wire the graph at startup.

## 4. Technology choices

| Layer | Default | Why | Alternatives behind interface |
|---|---|---|---|
| PDF parser | **Docling** (via docling-serve container) | Layout, tables, formulas, reading order; best open option for 2026. Runs as its own service so the API stays lean | MinerU, Unstructured |
| Chunker | Markdown structural | Chunks respect headings and tables; emits char offsets for citation highlighting | Fixed-size, semantic (Chonkie), LLM-chunker |
| Embedder | **BGE-M3** (sentence-transformers) | Multilingual, 1024-dim, strong recall, runs on CPU | nomic-embed-text-v1.5, Snowflake Arctic |
| Vector store | **LanceDB** | Embedded, columnar, zero-ops, great Python API | Qdrant single-node, sqlite-vec |
| Sparse index | **bm25s** | Pure-python, fast, no Java | tantivy-py, PySerini |
| Fusion | **RRF (k=60)** | Robust across score distributions | weighted sum, learned fuser |
| Reranker | **bge-reranker-v2-m3** | Highest-leverage single quality lever | Jina reranker, Cohere (cloud) |
| LLM | **Qwen2.5-7B-Instruct via Ollama** | Strong instruction follower at 7B, local-friendly | Llama 3.1, Phi-3, Mistral |
| API | **FastAPI + Pydantic v2** | Typed, async-native, OpenAPI free | — |
| UI | **Next.js 14 App Router + Tailwind** | Standalone output ships in a slim container | — |

## 5. Data layout (on disk)

```
./data/
  lancedb/             LanceDB table(s) — vectors + chunk metadata
  bm25/                serialized bm25s indices (per corpus)
  uploads/             raw uploaded source files
  eval_runs/           per-run JSON + markdown reports
  golden/qa.jsonl      eval golden set (user-managed)

./models/              HF cache (embedder, reranker weights)
```

All paths overridable via `.env` and bind-mounted into the containers.

## 6. API surface (v1)

```
GET  /health
GET  /api/v1/documents
POST /api/v1/documents/upload      (multipart)
DEL  /api/v1/documents/{doc_id}
POST /api/v1/chat/completions      (SSE stream of tokens + citations)
POST /api/v1/eval/run
GET  /api/v1/eval/runs/{run_id}
```

Chat completions always return citations as `SourceSpan` objects — `(doc_id, chunk_id, page, char_start, char_end)` — so the UI can highlight exact ranges in the source viewer, not just link to a page.

## 7. Quality strategy (the moat)

1. **Golden set per corpus type** (100–300 Q/A) checked into `data/golden/`.
2. **Retrieval metrics:** Recall@k, nDCG, MRR — deterministic, run on every CI build.
3. **Answer metrics:** faithfulness + citation precision via LLM judge (RAGAS-style, judge is Qwen2.5-7B so it stays local).
4. **Public benchmarks** run on tag: **FinanceBench**, **LegalBench-RAG**, **MultiHop-RAG**, **BEIR** subsets.
5. **Regression gate:** PRs touching retrieval must not drop any benchmark by >1pt without an explicit annotated waiver.

## 8. Security and privacy posture

- No telemetry. Opt-in only, and never on by default.
- No required outbound calls (model weights pre-pulled or fetched on first use from HF).
- CORS defaults restricted to `http://localhost:3000`.
- Containers run as non-root.
- Secrets (if ever added, e.g. for optional cloud providers) only via env.

## 9. Milestones

See [`ROADMAP.md`](ROADMAP.md).

## 10. Open questions

- Multi-tenant / collection isolation — needed for v1 or defer?
- Incremental re-index strategy for changed PDFs (hash-based diff vs. full rebuild)?
- ColPali-style visual retrieval as a second embedder — v2 feature or earlier?
- GraphRAG via Kuzu for multi-hop queries — compelling but risks scope creep.
