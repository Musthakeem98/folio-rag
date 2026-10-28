"""Stable ID generation for documents and chunks.

Doc IDs are derived from source + optional content hash so re-ingesting
the same file yields the same ID (and the vector store can upsert).
Chunk IDs are deterministic from doc ID + ordinal, so citations stay
stable across re-indexes.
"""

import hashlib
from pathlib import Path


def doc_id_for(source: str | Path, content: bytes | None = None) -> str:
    h = hashlib.sha256()
    h.update(str(source).encode("utf-8"))
    if content is not None:
        h.update(b"\x00")
        h.update(content)
    return h.hexdigest()[:16]


def chunk_id_for(doc_id: str, index: int) -> str:
    return f"{doc_id}:c{index:04d}"
