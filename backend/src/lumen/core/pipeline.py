"""End-to-end orchestration: ingest + query pipelines.

The pipeline composes component Protocols defined in each subpackage's base.py.
Implementations are selected by config and injected at construction time, not
discovered dynamically — this keeps the type graph legible.
"""

from dataclasses import dataclass
from pathlib import Path

from lumen.core.schemas import Answer, Document


@dataclass
class IngestPipeline:
    # parser, chunker, embedder, store — Protocol-typed, wired by factory

    async def run(self, source: Path | str) -> Document:
        raise NotImplementedError


@dataclass
class QueryPipeline:
    # retriever, reranker, generator — Protocol-typed, wired by factory

    async def run(self, query: str, k: int = 5) -> Answer:
        raise NotImplementedError
