"""Markdown-structural chunker.

Walks markdown by heading hierarchy, then packs each leaf section into
chunks that respect a target token budget. Tables and fenced code blocks
are kept whole whenever they fit — splitting them destroys retrieval
quality more than oversized chunks hurt it.

Token count is approximated as `max(1, round(words * 1.3))` which is
within ~10% of GPT/BGE tokenizer counts for English and avoids pulling
in a tokenizer dependency just for budget targeting.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from re import Match
from re import compile as re_compile

from app.core.ids import chunk_id_for
from app.core.schemas import Chunk

_HEADING_RE = re_compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_FENCE_RE = re_compile(r"^(```|~~~)")
_TABLE_ROW_RE = re_compile(r"^\s*\|.*\|\s*$")


def _approx_tokens(text: str) -> int:
    words = len(text.split())
    return max(1, round(words * 1.3))


@dataclass
class _Section:
    heading_path: list[str]
    char_start: int
    blocks: list[str] = field(default_factory=list)   # paragraphs / tables / code
    char_end: int = 0


def _iter_blocks(body: str, base_offset: int) -> Iterator[tuple[str, int, int]]:
    """Yield (block_text, char_start, char_end). Keeps fenced code and tables intact."""
    lines = body.splitlines(keepends=True)
    i = 0
    offset = base_offset
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            offset += len(line)
            i += 1
            continue

        start = offset
        if _FENCE_RE.match(stripped):
            # Fenced code block: consume until matching fence.
            buf = [line]
            offset += len(line)
            i += 1
            while i < len(lines) and not _FENCE_RE.match(lines[i].strip()):
                buf.append(lines[i])
                offset += len(lines[i])
                i += 1
            if i < len(lines):
                buf.append(lines[i])
                offset += len(lines[i])
                i += 1
            yield "".join(buf).rstrip("\n"), start, offset
        elif _TABLE_ROW_RE.match(line):
            # Table: consume consecutive table rows.
            buf = [line]
            offset += len(line)
            i += 1
            while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
                buf.append(lines[i])
                offset += len(lines[i])
                i += 1
            yield "".join(buf).rstrip("\n"), start, offset
        else:
            # Paragraph: consume until blank line.
            buf = [line]
            offset += len(line)
            i += 1
            while i < len(lines) and lines[i].strip() and not _FENCE_RE.match(lines[i].strip()):
                if _TABLE_ROW_RE.match(lines[i]):
                    break
                buf.append(lines[i])
                offset += len(lines[i])
                i += 1
            yield "".join(buf).rstrip("\n"), start, offset


def _split_sections(markdown: str) -> Iterator[_Section]:
    heading_stack: list[tuple[int, str]] = []
    section_start = 0
    section_body_start = 0
    section_path: list[str] = []

    lines = markdown.splitlines(keepends=True)
    pos = 0
    pending_blocks: list[tuple[str, int, int]] = []

    def flush(end: int) -> _Section | None:
        if not pending_blocks:
            return None
        s = _Section(heading_path=list(section_path), char_start=pending_blocks[0][1])
        s.blocks = [b for b, _, _ in pending_blocks]
        s.char_end = pending_blocks[-1][2]
        return s

    i = 0
    while i < len(lines):
        line = lines[i]
        m: Match[str] | None = _HEADING_RE.match(line.rstrip("\n"))
        if m:
            if pending_blocks:
                yield flush(pos)  # type: ignore[misc]
                pending_blocks = []

            level = len(m.group(1))
            title = m.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            section_path = [t for _, t in heading_stack]

            pos += len(line)
            section_start = pos
            section_body_start = pos
            i += 1
            continue

        # Collect blocks until next heading.
        body_chunk_start = pos
        body_lines: list[str] = []
        while i < len(lines) and not _HEADING_RE.match(lines[i].rstrip("\n")):
            body_lines.append(lines[i])
            pos += len(lines[i])
            i += 1
        body_text = "".join(body_lines)
        pending_blocks.extend(_iter_blocks(body_text, body_chunk_start))

    if pending_blocks:
        yield flush(pos)  # type: ignore[misc]


class MarkdownStructuralChunker:
    name = "markdown_structural"

    def __init__(
        self,
        target_tokens: int = 512,
        overlap_tokens: int = 64,
        preserve_tables: bool = True,
    ):
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        self.preserve_tables = preserve_tables

    def chunk(self, doc_id: str, markdown: str) -> Iterable[Chunk]:
        chunks: list[Chunk] = []
        index = 0
        for section in _split_sections(markdown):
            if section is None:
                continue
            for text, start, end in self._pack_blocks(section):
                chunks.append(
                    Chunk(
                        id=chunk_id_for(doc_id, index),
                        doc_id=doc_id,
                        text=text,
                        heading_path=section.heading_path,
                        char_start=start,
                        char_end=end,
                    )
                )
                index += 1
        return chunks

    def _pack_blocks(self, section: _Section) -> Iterator[tuple[str, int, int]]:
        """Greedy-pack blocks into chunks under the token budget, with overlap."""
        buf: list[str] = []
        buf_tokens = 0
        buf_start: int | None = None
        buf_end: int | None = None
        previous_tail: str = ""

        blocks = list(zip(section.blocks, _block_ranges(section)))
        heading_prefix = _heading_prefix(section.heading_path)
        header_tokens = _approx_tokens(heading_prefix) if heading_prefix else 0

        for block_text, (start, end) in blocks:
            block_tokens = _approx_tokens(block_text)
            if buf and buf_tokens + block_tokens + header_tokens > self.target_tokens:
                yield _assemble(heading_prefix, previous_tail, buf), buf_start or start, buf_end or end
                previous_tail = _tail(buf, self.overlap_tokens)
                buf, buf_tokens, buf_start, buf_end = [], 0, None, None

            if buf_start is None:
                buf_start = start
            buf_end = end
            buf.append(block_text)
            buf_tokens += block_tokens

        if buf:
            yield _assemble(heading_prefix, previous_tail, buf), buf_start or 0, buf_end or 0


def _block_ranges(section: _Section) -> list[tuple[int, int]]:
    # Reconstruct per-block (start, end) from section fields. The _iter_blocks
    # pass preserved offsets but we flattened to text; recompute by scanning.
    ranges: list[tuple[int, int]] = []
    pos = section.char_start
    for b in section.blocks:
        ranges.append((pos, pos + len(b)))
        pos += len(b) + 2  # approximate paragraph gap
    return ranges


def _heading_prefix(path: list[str]) -> str:
    return " > ".join(path) if path else ""


def _tail(buf: list[str], overlap_tokens: int) -> str:
    if overlap_tokens <= 0 or not buf:
        return ""
    words = (" ".join(buf)).split()
    tail_words = max(1, round(overlap_tokens / 1.3))
    return " ".join(words[-tail_words:])


def _assemble(heading_prefix: str, previous_tail: str, buf: list[str]) -> str:
    parts: list[str] = []
    if heading_prefix:
        parts.append(f"[{heading_prefix}]")
    if previous_tail:
        parts.append(previous_tail)
    parts.append("\n\n".join(buf))
    return "\n\n".join(parts).strip()
