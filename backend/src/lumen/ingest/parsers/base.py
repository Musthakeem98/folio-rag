from pathlib import Path
from typing import Protocol


class ParsedDocument(Protocol):
    """A parsed document — markdown body plus structural metadata."""

    source: str
    markdown: str
    pages: list[str]
    metadata: dict


class Parser(Protocol):
    """Converts a source (file path or URL) into structured markdown."""

    name: str

    async def parse(self, source: Path | str) -> ParsedDocument: ...
