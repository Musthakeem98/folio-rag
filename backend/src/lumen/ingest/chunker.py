"""Markdown-structural chunker.

Groups by heading hierarchy, then splits each section to a target token
budget while preserving tables and code blocks whole where possible.
"""

from collections.abc import Iterable

from lumen.core.schemas import Chunk


class MarkdownStructuralChunker:
    name = "markdown_structural"

    def __init__(self, target_tokens: int = 512, overlap_tokens: int = 64, preserve_tables: bool = True):
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        self.preserve_tables = preserve_tables

    def chunk(self, doc_id: str, markdown: str) -> Iterable[Chunk]:
        # TODO: heading-aware split + token-budget respecting join
        return []
