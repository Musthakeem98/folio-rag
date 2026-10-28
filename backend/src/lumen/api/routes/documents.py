from pathlib import Path

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel, Field

from lumen.api.deps import IngestDep, SettingsDep
from lumen.config import Settings
from lumen.core.pipeline import IngestPipeline

router = APIRouter(prefix="/documents", tags=["documents"])


class IngestURL(BaseModel):
    url: str = Field(..., pattern=r"^https?://")


@router.post("/upload")
async def upload(
    file: UploadFile,
    pipeline: IngestPipeline = IngestDep,
    settings: Settings = SettingsDep,
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename required")

    uploads = settings.data_dir / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    dest = uploads / Path(file.filename).name

    async with aiofiles.open(dest, "wb") as fh:
        while True:
            chunk = await file.read(1 << 20)
            if not chunk:
                break
            await fh.write(chunk)

    doc = await pipeline.run(dest)
    return {"status": "indexed", "doc_id": doc.id, "source": doc.source, "title": doc.title}


@router.post("/url")
async def ingest_url(req: IngestURL, pipeline: IngestPipeline = IngestDep) -> dict:
    doc = await pipeline.run(req.url)
    return {"status": "indexed", "doc_id": doc.id, "source": doc.source, "title": doc.title}


@router.get("")
async def list_documents(pipeline: IngestPipeline = IngestDep) -> list[dict]:
    chunks = await pipeline.store.all_chunks()
    by_doc: dict[str, dict] = {}
    for c in chunks:
        d = by_doc.setdefault(c.doc_id, {"id": c.doc_id, "chunks": 0, "source": c.metadata.get("source", "")})
        d["chunks"] += 1
    return list(by_doc.values())


@router.delete("/{doc_id}")
async def delete(doc_id: str, pipeline: IngestPipeline = IngestDep) -> dict:
    await pipeline.store.delete(doc_id)
    if pipeline.sparse is not None:
        remaining = await pipeline.store.all_chunks()
        await pipeline.sparse.refit(remaining)
    return {"status": "deleted", "doc_id": doc_id}
