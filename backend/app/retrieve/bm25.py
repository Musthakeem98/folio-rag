"""BM25 sparse retrieval via bm25s (fast, pure-python, no Java).

Index persistence: bm25s has native save/load. We keep the index on
disk alongside the LanceDB table and reload on first retrieval.

Updates: bm25s doesn't support true incremental indexing, so after each
ingest we rebuild from the full chunk list in the vector store. For
personal/offline corpus sizes this is well under a second; a Phase 2+
optimization will shard the sparse index when it becomes relevant.
"""

import asyncio
import pickle
from pathlib import Path
from typing import Any

from app.core.schemas import Chunk, RetrievedChunk


class BM25Retriever:
    name = "bm25s"

    def __init__(self, path: Path, top_k: int = 50):
        self.path = Path(path)
        self.top_k = top_k
        self._index: Any | None = None
        self._chunk_order: list[Chunk] = []

    async def refit(self, chunks: list[Chunk]) -> None:
        """Rebuild the sparse index from the current full chunk list."""
        await asyncio.to_thread(self._refit_sync, chunks)

    def _refit_sync(self, chunks: list[Chunk]) -> None:
        import bm25s

        if not chunks:
            self._index = None
            self._chunk_order = []
            self._persist()
            return

        corpus = [c.text for c in chunks]
        tokens = bm25s.tokenize(corpus, stopwords="en", show_progress=False)
        idx = bm25s.BM25()
        idx.index(tokens, show_progress=False)
        self._index = idx
        self._chunk_order = list(chunks)
        self._persist()

    async def retrieve(self, query: str) -> list[RetrievedChunk]:
        if self._index is None:
            await asyncio.to_thread(self._load)
        if self._index is None or not self._chunk_order:
            return []
        return await asyncio.to_thread(self._retrieve_sync, query)

    def _retrieve_sync(self, query: str) -> list[RetrievedChunk]:
        import bm25s

        q_tokens = bm25s.tokenize([query], stopwords="en", show_progress=False)
        docs, scores = self._index.retrieve(q_tokens, k=min(self.top_k, len(self._chunk_order)))
        hits: list[RetrievedChunk] = []
        for rank, (idx, score) in enumerate(zip(docs[0], scores[0], strict=True)):
            hits.append(RetrievedChunk(chunk=self._chunk_order[int(idx)], score=float(score), rank=rank))
        return hits

    def _persist(self) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        if self._index is None:
            # Clear the file to signal "no index yet".
            (self.path / "chunks.pkl").write_bytes(b"")
            return
        self._index.save(str(self.path / "bm25"))
        with (self.path / "chunks.pkl").open("wb") as fh:
            pickle.dump(self._chunk_order, fh)

    def _load(self) -> None:
        import bm25s

        chunks_file = self.path / "chunks.pkl"
        if not chunks_file.exists() or chunks_file.stat().st_size == 0:
            return
        try:
            self._index = bm25s.BM25.load(str(self.path / "bm25"))
            with chunks_file.open("rb") as fh:
                self._chunk_order = pickle.load(fh)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            self._index = None
            self._chunk_order = []
