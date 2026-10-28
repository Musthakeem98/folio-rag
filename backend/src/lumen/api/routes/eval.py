from fastapi import APIRouter

router = APIRouter(prefix="/eval", tags=["eval"])


@router.post("/run")
async def run() -> dict[str, str]:
    # TODO: trigger eval runner against configured golden set
    return {"status": "queued"}


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict[str, str]:
    # TODO: return metrics + per-question breakdown
    return {"run_id": run_id, "status": "pending"}
