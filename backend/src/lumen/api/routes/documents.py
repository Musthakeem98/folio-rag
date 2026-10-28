from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload(file: UploadFile) -> dict[str, str]:
    # TODO: persist to data dir, enqueue ingest job
    return {"status": "accepted", "filename": file.filename or ""}


@router.get("")
async def list_documents() -> list[dict[str, str]]:
    # TODO: query store metadata
    return []


@router.delete("/{doc_id}")
async def delete(doc_id: str) -> dict[str, str]:
    # TODO: remove from store + sparse index
    return {"status": "deleted", "doc_id": doc_id}
