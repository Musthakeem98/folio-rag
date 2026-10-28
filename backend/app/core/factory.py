"""Build pipelines from Settings. One place, obvious wiring, no DI framework."""

from app.config import Settings
from app.core.pipeline import IngestPipeline
from app.embed.sentence_transformer import SentenceTransformerEmbedder
from app.ingest.chunker import MarkdownStructuralChunker
from app.ingest.parsers.markdown import MarkdownParser
from app.ingest.parsers.pdf_docling import DoclingParser
from app.ingest.parsers.web import WebParser
from app.retrieve.bm25 import BM25Retriever
from app.store.lancedb_store import LanceDBStore


def build_ingest_pipeline(settings: Settings) -> IngestPipeline:
    embedder = SentenceTransformerEmbedder(
        model=settings.embed_model,
        device=settings.embed_device,
    )
    store = LanceDBStore(path=settings.lancedb_path, dim=embedder.dim)
    sparse = BM25Retriever(path=settings.data_dir / "bm25")
    chunker = MarkdownStructuralChunker()
    parsers = {
        "pdf": DoclingParser(host=settings.docling_host),
        "web": WebParser(),
        "markdown": MarkdownParser(),
    }
    return IngestPipeline(parsers=parsers, chunker=chunker, embedder=embedder, store=store, sparse=sparse)
