"""Cross-encoder reranker — the single highest-leverage quality lever."""

from app.core.schemas import RetrievedChunk


class CrossEncoderReranker:
    name = "bge_reranker_v2_m3"

    def __init__(self, model: str = "BAAI/bge-reranker-v2-m3", top_k: int = 5):
        self.model = model
        self.top_k = top_k
        self._model = None

    async def rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
        # TODO: cross-encoder scoring over (query, chunk.text) pairs
        return candidates[: self.top_k]
