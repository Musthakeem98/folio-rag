"""sentence-transformers backed embedder.

Default model is BAAI/bge-m3 — multilingual, 1024-dim, strong on both
retrieval and reranking benchmarks, runs on CPU acceptably.
"""


class SentenceTransformerEmbedder:
    name = "sentence_transformers"

    def __init__(self, model: str = "BAAI/bge-m3", device: str = "cpu", batch_size: int = 32, normalize: bool = True):
        self.model = model
        self.device = device
        self.batch_size = batch_size
        self.normalize = normalize
        self.dim = 1024
        self._model = None  # lazy

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # TODO: lazy-load SentenceTransformer and encode in batches
        return [[0.0] * self.dim for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        return [0.0] * self.dim
