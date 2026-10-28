from pathlib import Path

from app.config import Settings
from app.core.factory import build_ingest_pipeline


def test_factory_wires_full_graph(tmp_path: Path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        lancedb_path=tmp_path / "lancedb",
        embed_device="cpu",
    )
    pipeline = build_ingest_pipeline(settings)

    assert set(pipeline.parsers.keys()) == {"pdf", "web", "markdown"}
    assert pipeline.chunker is not None
    assert pipeline.embedder is not None
    assert pipeline.store is not None
    assert pipeline.sparse is not None
