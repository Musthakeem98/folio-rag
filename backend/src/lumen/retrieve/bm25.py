"""BM25 sparse retrieval via bm25s (fast, pure-python, no Java)."""

from lumen.core.schemas import Chunk, RetrievedChunk


class BM25Retriever:
    name = "bm25s"

    def __init__(self, top_k: int = 50):
        self.top_k = top_k
        self._index = None  # bm25s.BM25

    def fit(self, chunks: list[Chunk]) -> None:
        # TODO: tokenize + build bm25s index, persist alongside LanceDB
        return None

    async def retrieve(self, query: str) -> list[RetrievedChunk]:
        return []
