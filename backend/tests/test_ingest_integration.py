"""End-to-end ingest test with a fake embedder (no model download) and real LanceDB."""

from pathlib import Path

import pytest

from lumen.core.pipeline import IngestPipeline
from lumen.ingest.chunker import MarkdownStructuralChunker
from lumen.ingest.parsers.markdown import MarkdownParser
from lumen.retrieve.bm25 import BM25Retriever
from lumen.store.lancedb_store import LanceDBStore

FIXTURE = Path(__file__).parent / "fixtures" / "sample.md"


class _FakeEmbedder:
    """Deterministic fake: tiny dim, hashes text to a vector. No model download."""

    name = "fake"
    dim = 8

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        return self._vec(text)

    def _vec(self, text: str) -> list[float]:
        h = abs(hash(text))
        return [((h >> (i * 4)) & 0xF) / 15.0 for i in range(self.dim)]


@pytest.mark.asyncio
async def test_ingest_end_to_end(tmp_path: Path) -> None:
    embedder = _FakeEmbedder()
    store = LanceDBStore(path=tmp_path / "lancedb", dim=embedder.dim)
    sparse = BM25Retriever(path=tmp_path / "bm25")
    pipeline = IngestPipeline(
        parsers={"markdown": MarkdownParser()},
        chunker=MarkdownStructuralChunker(target_tokens=120),
        embedder=embedder,
        store=store,
        sparse=sparse,
    )

    doc = await pipeline.run(FIXTURE)
    assert doc.id
    assert doc.source.endswith("sample.md")

    all_chunks = await store.all_chunks()
    assert all_chunks, "store should contain chunks after ingest"
    assert all(c.doc_id == doc.id for c in all_chunks)

    # Sparse index should return hits for a known phrase.
    hits = await sparse.retrieve("legal hold")
    assert hits, "bm25 should match the exceptions section"
    assert "legal hold" in hits[0].chunk.text.lower()

    # Re-ingest the same doc: chunk count should not grow (upsert-by-doc).
    before = len(all_chunks)
    await pipeline.run(FIXTURE)
    after = len(await store.all_chunks())
    assert after == before, f"re-ingest should be idempotent, got {before} -> {after}"
