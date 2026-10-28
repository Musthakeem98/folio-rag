"""Docling-based PDF parser.

Docling handles layout, tables, formulas, and reading order — the parts
that make PDF RAG actually work. We intentionally do not fall back to
PyPDF for malformed files; it loses too much structure.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DoclingParsed:
    source: str
    markdown: str
    pages: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class DoclingParser:
    name = "docling"

    def __init__(self, extract_tables: bool = True, extract_figures: bool = True, ocr: str = "auto"):
        self.extract_tables = extract_tables
        self.extract_figures = extract_figures
        self.ocr = ocr

    async def parse(self, source: Path | str) -> DoclingParsed:
        # TODO: wire docling.DocumentConverter
        return DoclingParsed(source=str(source), markdown="")
