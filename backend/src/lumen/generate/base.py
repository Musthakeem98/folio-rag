from collections.abc import AsyncIterator
from typing import Protocol

from lumen.core.schemas import RetrievedChunk


class Generator(Protocol):
    name: str

    async def generate(self, query: str, context: list[RetrievedChunk], system: str) -> str: ...
    async def stream(self, query: str, context: list[RetrievedChunk], system: str) -> AsyncIterator[str]: ...
