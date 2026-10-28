from collections.abc import AsyncIterator

from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    k: int = 5
    stream: bool = True


@router.post("/completions")
async def completions(req: ChatRequest) -> EventSourceResponse:
    async def event_stream() -> AsyncIterator[dict[str, str]]:
        # TODO: run QueryPipeline, stream LLM tokens + final citations event
        yield {"event": "token", "data": "stub"}
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_stream())
