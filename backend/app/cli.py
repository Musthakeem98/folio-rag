import asyncio
from pathlib import Path

import typer
from rich.console import Console

from app.config import get_settings
from app.core.factory import build_ingest_pipeline

app = typer.Typer(help="Folio — local-first RAG CLI.", no_args_is_help=True)
console = Console()


_SUPPORTED_EXT = {".pdf", ".md", ".markdown", ".txt"}


def _iter_sources(source: str) -> list[str]:
    if source.startswith(("http://", "https://")):
        return [source]
    p = Path(source)
    if not p.exists():
        raise typer.BadParameter(f"not found: {source}")
    if p.is_file():
        return [str(p)]
    return [str(f) for f in sorted(p.rglob("*")) if f.suffix.lower() in _SUPPORTED_EXT]


@app.command()
def index(
    source: str = typer.Argument(..., help="File, directory, or URL to index."),
) -> None:
    """Parse, chunk, embed, and persist documents."""
    settings = get_settings()
    pipeline = build_ingest_pipeline(settings)
    sources = _iter_sources(source)
    console.print(f"[cyan]indexing {len(sources)} source(s)[/]")

    async def _run_all() -> None:
        for s in sources:
            try:
                doc = await pipeline.run(s)
                console.print(f"  [green]ok[/] {s}  →  {doc.id}")
            except Exception as e:  # noqa: BLE001
                console.print(f"  [red]fail[/] {s}  →  {type(e).__name__}: {e}")

    asyncio.run(_run_all())


@app.command()
def ask(
    query: str = typer.Argument(...),
    k: int = typer.Option(5, "--k"),
) -> None:
    """Run a one-shot query against the index. (wired in Phase 3)"""
    console.print(f"[yellow]query path not yet wired. would run:[/] {query!r}  k={k}")


@app.command("eval")
def run_eval(
    config: Path = typer.Option(Path("configs/folio.default.yaml"), "--config", "-c"),
) -> None:
    """Run the golden-set eval harness. (wired in Phase 3)"""
    console.print(f"[yellow]eval harness not yet wired. config={config}[/]")


if __name__ == "__main__":
    app()
