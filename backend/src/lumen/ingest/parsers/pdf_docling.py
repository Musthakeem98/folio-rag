"""Docling parser — thin HTTP client to the docling-serve container.

Docling runs as its own service so the API image stays slim (no torch,
no layout/OCR model weights) and so GPU can be scoped to parsing only.
See docker-compose.yml for the `docling` service.

docling-serve API shape may vary across releases — verify endpoint path
and response fields against the running image before shipping.
"""

from dataclasses import dataclass, field
from pathlib import Path

import httpx


@dataclass
class DoclingParsed:
    source: str
    markdown: str
    pages: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class DoclingParser:
    name = "docling"

    def __init__(
        self,
        host: str,
        extract_tables: bool = True,
        extract_figures: bool = True,
        ocr: str = "auto",
        timeout: float = 300.0,
    ):
        self.host = host.rstrip("/")
        self.extract_tables = extract_tables
        self.extract_figures = extract_figures
        self.ocr = ocr
        self.timeout = timeout

    async def parse(self, source: Path | str) -> DoclingParsed:
        path = Path(source)
        options = {
            "to_formats": ["md"],
            "do_ocr": self.ocr != "never",
            "do_table_structure": self.extract_tables,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            with path.open("rb") as fh:
                r = await client.post(
                    f"{self.host}/v1alpha/convert/file",
                    files={"files": (path.name, fh, "application/pdf")},
                    data={"options": _json(options)},
                )
            r.raise_for_status()
            body = r.json()

        md, pages, meta = _extract(body)
        return DoclingParsed(source=str(source), markdown=md, pages=pages, metadata=meta)


def _json(v: dict) -> str:
    import json

    return json.dumps(v)


def _extract(body: dict) -> tuple[str, list[str], dict]:
    # docling-serve response envelope varies by version. Handle the common
    # shapes; fall back to empty strings so downstream chunker degrades gracefully.
    document = body.get("document") or body.get("result") or body
    md = document.get("md_content") or document.get("markdown") or ""
    pages = document.get("pages") or []
    meta = {k: v for k, v in document.items() if k not in {"md_content", "markdown", "pages"}}
    return md, pages, meta
