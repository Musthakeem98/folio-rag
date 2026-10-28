"""Ollama HTTP client — keeps the local-first promise."""

from collections.abc import AsyncIterator

import httpx

from lumen.core.schemas import RetrievedChunk


class OllamaGenerator:
    name = "ollama"

    def __init__(self, host: str, model: str, temperature: float = 0.2, max_tokens: int = 1024):
        self.host = host.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _build_prompt(self, query: str, context: list[RetrievedChunk]) -> str:
        ctx = "\n\n".join(f"[{c.chunk.id}] {c.chunk.text}" for c in context)
        return f"Context:\n{ctx}\n\nQuestion: {query}\n\nAnswer:"

    async def generate(self, query: str, context: list[RetrievedChunk], system: str) -> str:
        prompt = self._build_prompt(query, context)
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {"temperature": self.temperature, "num_predict": self.max_tokens},
                },
            )
            r.raise_for_status()
            return r.json().get("response", "")

    async def stream(self, query: str, context: list[RetrievedChunk], system: str) -> AsyncIterator[str]:
        prompt = self._build_prompt(query, context)
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": True,
                    "options": {"temperature": self.temperature, "num_predict": self.max_tokens},
                },
            ) as r:
                async for line in r.aiter_lines():
                    if line:
                        yield line
