from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Lumen — local-first RAG CLI.", no_args_is_help=True)
console = Console()


@app.command()
def index(
    source: Path = typer.Argument(..., exists=True, help="File or directory to index."),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Parse, chunk, embed, and persist documents."""
    console.print(f"[bold cyan]index[/] {source}  (config={config})")
    console.print("[yellow]TODO:[/] wire ingest pipeline")


@app.command()
def ask(
    query: str = typer.Argument(...),
    k: int = typer.Option(5, "--k"),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Run a one-shot query against the index."""
    console.print(f"[bold cyan]ask[/] {query!r}  k={k}")
    console.print("[yellow]TODO:[/] wire retrieve+generate pipeline")


@app.command("eval")
def run_eval(
    config: Path = typer.Option(Path("configs/lumen.default.yaml"), "--config", "-c"),
) -> None:
    """Run the golden-set eval harness."""
    console.print(f"[bold cyan]eval[/] config={config}")
    console.print("[yellow]TODO:[/] wire eval runner")


if __name__ == "__main__":
    app()
