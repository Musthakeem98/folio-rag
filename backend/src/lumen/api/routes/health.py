from fastapi import APIRouter

from lumen import __version__

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
