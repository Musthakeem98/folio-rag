"""LanceDB vector store — embedded, zero-ops, columnar on disk."""

from pathlib import Path

from lumen.core.schemas import Chunk


class LanceDBStore:
    name = "lancedb"

    def __init__(self, path: Path, table: str = "documents", metric: str = "cosine"):
        self.path = Path(path)
        self.table = table
        self.metric = metric
        self._db = None  # lazy

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        # TODO: open table, batch upsert via pyarrow
        return None

    async def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[tuple[Chunk, float]]:
        # TODO: KNN with optional metadata filter
        return []

    async def delete(self, doc_id: str) -> None:
        return None
