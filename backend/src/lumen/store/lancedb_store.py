"""LanceDB vector store — embedded, columnar, zero-ops.

Upsert semantics: delete-by-doc-id then append. This keeps re-indexing
idempotent without needing LanceDB's `merge_insert` API (which varies
across versions).
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import pyarrow as pa

from lumen.core.schemas import Chunk


def _schema(dim: int) -> pa.Schema:
    return pa.schema(
        [
            pa.field("id", pa.string()),
            pa.field("doc_id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("page", pa.int32()),
            pa.field("heading_path", pa.list_(pa.string())),
            pa.field("char_start", pa.int32()),
            pa.field("char_end", pa.int32()),
            pa.field("metadata", pa.string()),  # JSON blob
            pa.field("vector", pa.list_(pa.float32(), dim)),
        ]
    )


class LanceDBStore:
    name = "lancedb"

    def __init__(self, path: Path, table: str = "documents", dim: int = 1024, metric: str = "cosine"):
        self.path = Path(path)
        self.table_name = table
        self.dim = dim
        self.metric = metric
        self._db: Any | None = None

    def _ensure_db(self) -> Any:
        if self._db is None:
            import lancedb

            self.path.mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(str(self.path))
        return self._db

    def _ensure_table(self) -> Any:
        db = self._ensure_db()
        try:
            return db.open_table(self.table_name)
        except (FileNotFoundError, ValueError):
            return db.create_table(self.table_name, schema=_schema(self.dim))

    async def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if not chunks:
            return
        await asyncio.to_thread(self._upsert_sync, chunks, vectors)

    def _upsert_sync(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        tbl = self._ensure_table()
        doc_ids = sorted({c.doc_id for c in chunks})
        for doc_id in doc_ids:
            escaped = doc_id.replace("'", "''")
            tbl.delete(f"doc_id = '{escaped}'")
        rows = [
            {
                "id": c.id,
                "doc_id": c.doc_id,
                "text": c.text,
                "page": c.page if c.page is not None else -1,
                "heading_path": c.heading_path,
                "char_start": c.char_start if c.char_start is not None else -1,
                "char_end": c.char_end if c.char_end is not None else -1,
                "metadata": json.dumps(c.metadata) if c.metadata else "{}",
                "vector": vec,
            }
            for c, vec in zip(chunks, vectors, strict=True)
        ]
        tbl.add(rows)

    async def search(self, vector: list[float], k: int, filters: dict | None = None) -> list[tuple[Chunk, float]]:
        return await asyncio.to_thread(self._search_sync, vector, k, filters)

    def _search_sync(self, vector: list[float], k: int, filters: dict | None) -> list[tuple[Chunk, float]]:
        tbl = self._ensure_table()
        q = tbl.search(vector).metric(self.metric).limit(k)
        if filters:
            for field, value in filters.items():
                escaped = str(value).replace("'", "''")
                q = q.where(f"{field} = '{escaped}'")
        hits = q.to_list()
        return [(_row_to_chunk(r), float(r.get("_distance", 0.0))) for r in hits]

    async def delete(self, doc_id: str) -> None:
        await asyncio.to_thread(self._delete_sync, doc_id)

    def _delete_sync(self, doc_id: str) -> None:
        tbl = self._ensure_table()
        escaped = doc_id.replace("'", "''")
        tbl.delete(f"doc_id = '{escaped}'")

    async def all_chunks(self) -> list[Chunk]:
        """Return every chunk in the store. Used by BM25 to rebuild the sparse index."""
        return await asyncio.to_thread(self._all_chunks_sync)

    def _all_chunks_sync(self) -> list[Chunk]:
        tbl = self._ensure_table()
        arrow_tbl = tbl.to_arrow() if hasattr(tbl, "to_arrow") else tbl.to_lance().to_table()
        rows = arrow_tbl.drop(["vector"]).to_pylist()
        return [_row_to_chunk(r) for r in rows]


def _row_to_chunk(r: dict) -> Chunk:
    meta_raw = r.get("metadata") or "{}"
    try:
        meta = json.loads(meta_raw) if isinstance(meta_raw, str) else dict(meta_raw)
    except json.JSONDecodeError:
        meta = {}
    page = r.get("page")
    char_start = r.get("char_start")
    char_end = r.get("char_end")
    return Chunk(
        id=r["id"],
        doc_id=r["doc_id"],
        text=r["text"],
        page=None if page in (None, -1) else int(page),
        heading_path=list(r.get("heading_path") or []),
        char_start=None if char_start in (None, -1) else int(char_start),
        char_end=None if char_end in (None, -1) else int(char_end),
        metadata=meta,
    )
