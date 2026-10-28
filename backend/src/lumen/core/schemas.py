from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceSpan(BaseModel):
    """A located span of source text — the atomic unit of citation."""

    doc_id: str
    chunk_id: str
    page: int | None = None
    char_start: int | None = None
    char_end: int | None = None


class Chunk(BaseModel):
    id: str
    doc_id: str
    text: str
    page: int | None = None
    heading_path: list[str] = Field(default_factory=list)
    char_start: int | None = None
    char_end: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    id: str
    source: str              # path or URL
    title: str | None = None
    mime_type: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float
    rank: int


class Answer(BaseModel):
    query: str
    text: str
    citations: list[SourceSpan] = Field(default_factory=list)
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    latency_ms: float | None = None
