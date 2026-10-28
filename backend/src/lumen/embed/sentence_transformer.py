"""sentence-transformers backed embedder.

Default model is BAAI/bge-m3 — multilingual, 1024-dim, strong on retrieval
benchmarks, runs acceptably on CPU for personal/offline corpora.

The model is lazy-loaded on first embed call so API startup stays fast
and tests that don't exercise embedding don't pull hundreds of MB of
weights off disk.
"""

import asyncio
from typing import Any


class SentenceTransformerEmbedder:
    name = "sentence_transformers"

    _MODEL_DIMS = {
        "BAAI/bge-m3": 1024,
        "BAAI/bge-large-en-v1.5": 1024,
        "BAAI/bge-base-en-v1.5": 768,
        "intfloat/e5-large-v2": 1024,
        "nomic-ai/nomic-embed-text-v1.5": 768,
    }

    def __init__(
        self,
        model: str = "BAAI/bge-m3",
        device: str = "cpu",
        batch_size: int = 32,
        normalize: bool = True,
    ):
        self.model_name = model
        self.device = device
        self.batch_size = batch_size
        self.normalize = normalize
        self.dim = self._MODEL_DIMS.get(model, 1024)
        self._model: Any | None = None

    def _ensure_loaded(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
            # Prefer the model's reported dim over our table.
            try:
                self.dim = self._model.get_sentence_embedding_dimension()
            except Exception:
                pass
        return self._model

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._encode, texts)

    async def embed_query(self, text: str) -> list[float]:
        vecs = await asyncio.to_thread(self._encode, [text])
        return vecs[0]

    def _encode(self, texts: list[str]) -> list[list[float]]:
        model = self._ensure_loaded()
        arr = model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return arr.tolist()
