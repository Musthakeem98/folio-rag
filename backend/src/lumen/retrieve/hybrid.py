"""Hybrid retrieval: dense + sparse fused with Reciprocal Rank Fusion."""

from collections import defaultdict

from lumen.core.schemas import RetrievedChunk
from lumen.retrieve.bm25 import BM25Retriever
from lumen.retrieve.dense import DenseRetriever


class HybridRetriever:
    def __init__(self, dense: DenseRetriever, sparse: BM25Retriever, rrf_k: int = 60):
        self.dense = dense
        self.sparse = sparse
        self.rrf_k = rrf_k

    async def retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        dense_hits = await self.dense.retrieve(query)
        sparse_hits = await self.sparse.retrieve(query)

        scores: dict[str, float] = defaultdict(float)
        chunks: dict[str, RetrievedChunk] = {}
        for hits in (dense_hits, sparse_hits):
            for h in hits:
                scores[h.chunk.id] += 1.0 / (self.rrf_k + h.rank + 1)
                chunks[h.chunk.id] = h

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:k]
        return [
            RetrievedChunk(chunk=chunks[cid].chunk, score=score, rank=i)
            for i, (cid, score) in enumerate(ranked)
        ]
