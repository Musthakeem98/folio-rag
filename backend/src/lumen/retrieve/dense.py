from lumen.core.schemas import RetrievedChunk
from lumen.embed.base import Embedder
from lumen.store.base import VectorStore


class DenseRetriever:
    def __init__(self, embedder: Embedder, store: VectorStore, top_k: int = 50):
        self.embedder = embedder
        self.store = store
        self.top_k = top_k

    async def retrieve(self, query: str, filters: dict | None = None) -> list[RetrievedChunk]:
        vec = await self.embedder.embed_query(query)
        hits = await self.store.search(vec, k=self.top_k, filters=filters)
        return [RetrievedChunk(chunk=c, score=s, rank=i) for i, (c, s) in enumerate(hits)]
