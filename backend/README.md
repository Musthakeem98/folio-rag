# Lumen backend

FastAPI service + Typer CLI for the Lumen RAG pipeline.

## Local dev

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run API
uvicorn lumen.main:app --reload --port 8000

# Or use the CLI
lumen --help
lumen index ./sample_docs
lumen ask "What is the retention period?"
lumen eval --config ../configs/lumen.default.yaml
```

## Layout

```
src/lumen/
  main.py          FastAPI app factory
  config.py        Pydantic settings (env + YAML)
  cli.py           Typer CLI (index, ask, eval)
  api/             HTTP routes
  core/            Pipeline orchestration, shared schemas
  ingest/          Parsers + chunker
  embed/           Embedding providers
  store/           Vector + sparse index backends
  retrieve/        Dense, sparse, hybrid fusion, reranking
  generate/        LLM providers (Ollama default)
  eval/            Metrics + benchmark runners
```

Every subpackage exposes a `base.py` with a Protocol/ABC — implementations are swapped via config, not kwargs.
