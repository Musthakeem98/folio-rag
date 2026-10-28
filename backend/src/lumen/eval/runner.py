"""Golden-set eval runner.

Reads a JSONL of {query, relevant_chunk_ids, reference_answer}, runs the
configured QueryPipeline, computes retrieval + answer metrics, and emits
a run report (JSON + markdown) under ./data/eval_runs/.
"""

from pathlib import Path

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def run(
    config: Path = typer.Option(Path("configs/lumen.default.yaml"), "--config", "-c"),
    golden: Path | None = typer.Option(None, "--golden"),
    out: Path = typer.Option(Path("data/eval_runs"), "--out"),
) -> None:
    typer.echo(f"TODO: load pipeline from {config}, evaluate {golden or 'default'}, write to {out}")


if __name__ == "__main__":
    app()
