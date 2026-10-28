from typing import Protocol

from lumen.core.schemas import Chunk


class VectorStore(Protocol):
    name: str

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...
    async def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[tuple[Chunk, float]]: ...
    async def delete(self, doc_id: str) -> None: ...
