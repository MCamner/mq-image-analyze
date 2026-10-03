"""CLI command: perceive — produce a perception.v1 record for Release Gate v2."""
from __future__ import annotations

import json
from pathlib import Path

import typer


def perceive_cmd(
    image_path: str = typer.Argument(..., help="Path to screenshot, UI or diagram."),
    producer: str = typer.Option(..., "--producer", "-p", help="ui | architecture | ocr"),
    source_type: str | None = typer.Option(
        None,
        "--source-type",
        help="screenshot | diagram | ui | terminal | browser. Required for ocr.",
    ),
    out: Path | None = typer.Option(None, "--out", "-o", help="Write the record to this file instead of stdout."),
) -> None:
    """Run one producer and print a normalized perception.v1 record."""
    from mq_image_analyze.perception import perceive

    p = Path(image_path).expanduser().resolve()
    if not p.is_file():
        typer.echo(f"File not found: {p}", err=True)
        raise typer.Exit(1)

    try:
        record = perceive(p, producer=producer, source_type=source_type, source_path=image_path)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    text = json.dumps(record, indent=2)
    if out is None:
        typer.echo(text)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    typer.echo(f"Wrote {out}", err=True)
