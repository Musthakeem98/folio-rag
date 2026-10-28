from pathlib import Path

from lumen.ingest.chunker import MarkdownStructuralChunker

FIXTURE = Path(__file__).parent / "fixtures" / "sample.md"


def test_produces_chunks() -> None:
    md = FIXTURE.read_text(encoding="utf-8")
    chunker = MarkdownStructuralChunker(target_tokens=120, overlap_tokens=20)
    chunks = list(chunker.chunk("doc0001", md))

    assert chunks, "chunker should produce at least one chunk"
    assert all(c.doc_id == "doc0001" for c in chunks)
    assert all(c.id.startswith("doc0001:c") for c in chunks)
    assert len([c.id for c in chunks]) == len({c.id for c in chunks}), "chunk ids must be unique"


def test_preserves_heading_hierarchy() -> None:
    md = FIXTURE.read_text(encoding="utf-8")
    chunker = MarkdownStructuralChunker(target_tokens=120)
    chunks = list(chunker.chunk("d", md))

    # The "Exceptions" subsection sits under "Timelines" under "Retention Policy".
    exceptions = [c for c in chunks if "legal hold" in c.text.lower()]
    assert exceptions, "expected a chunk covering the legal-hold text"
    path = exceptions[0].heading_path
    assert path[-3:] == ["Retention Policy", "Timelines", "Exceptions"], path


def test_heading_prefix_appears_in_text() -> None:
    md = FIXTURE.read_text(encoding="utf-8")
    chunker = MarkdownStructuralChunker(target_tokens=120)
    chunks = list(chunker.chunk("d", md))
    deletion = [c for c in chunks if "thirty-day" in c.text]
    assert deletion, "expected deletion chunk"
    # Heading prefix is embedded so retrieval surfaces section context.
    assert "Deletion" in deletion[0].text


def test_empty_input_returns_no_chunks() -> None:
    chunker = MarkdownStructuralChunker()
    assert list(chunker.chunk("d", "")) == []
