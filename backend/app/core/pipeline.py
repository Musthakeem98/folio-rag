"""End-to-end orchestration: ingest + query pipelines.

Pipelines compose component Protocols defined in each subpackage's base.py.
Implementations are selected by config and injected at construction time,
not discovered dynamically — the type graph stays legible this way.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.ids import doc_id_for
from app.core.schemas import Answer, Chunk, Document


@dataclass
class IngestPipeline:
    parsers: dict[str, Any]      # "pdf" | "web" | "markdown" -> Parser-shaped object
    chunker: Any                 # Chunker (duck-typed)
    embedder: Any                # Embedder
    store: Any                   # VectorStore
    sparse: Any | None = None    # BM25Retriever

    def _pick_parser(self, source: Path | str) -> Any:
        s = str(source)
        if s.startswith(("http://", "https://")):
            return self.parsers["web"]
        lower = s.lower()
        if lower.endswith(".pdf"):
            return self.parsers["pdf"]
        if lower.endswith((".md", ".markdown", ".txt")):
            return self.parsers["markdown"]
        raise ValueError(f"no parser registered for source: {source}")

    async def run(self, source: Path | str) -> Document:
        parser = self._pick_parser(source)
        parsed = await parser.parse(source)

        doc_id = doc_id_for(source)
        doc = Document(
            id=doc_id,
            source=str(source),
            title=parsed.metadata.get("title") if isinstance(parsed.metadata, dict) else None,
            metadata=parsed.metadata if isinstance(parsed.metadata, dict) else {},
        )

        chunks: list[Chunk] = list(self.chunker.chunk(doc_id, parsed.markdown))
        if not chunks:
            return doc

        vectors = await self.embedder.embed_documents([c.text for c in chunks])
        await self.store.upsert(chunks, vectors)

        if self.sparse is not None:
            all_chunks = await self.store.all_chunks()
            await self.sparse.refit(all_chunks)

        return doc


@dataclass
class QueryPipeline:
    retriever: Any
    reranker: Any
    generator: Any

    async def run(self, query: str, k: int = 5) -> Answer:
        raise NotImplementedError("query pipeline is wired in Phase 3")
