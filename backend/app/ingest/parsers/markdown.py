"""Passthrough parser for .md / .markdown / .txt files."""

from dataclasses import dataclass, field
from pathlib import Path

import aiofiles


@dataclass
class MarkdownParsed:
    source: str
    markdown: str
    pages: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class MarkdownParser:
    name = "markdown"

    async def parse(self, source: Path | str) -> MarkdownParsed:
        path = Path(source)
        async with aiofiles.open(path, encoding="utf-8", errors="replace") as fh:
            text = await fh.read()
        return MarkdownParsed(source=str(source), markdown=text, metadata={"size": len(text)})
