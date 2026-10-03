"""CLI command: ocr — produce image_ocr.v1, the same payload as the image_ocr MCP tool."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import typer


def ocr_cmd(
    image_path: str = typer.Argument(..., help="Path to image."),
    json_output: bool = typer.Option(False, "--json", help="Print image_ocr.v1 JSON."),
) -> None:
    """Extract visible text from an image."""
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr

    p = Path(image_path).expanduser().resolve()
    if not p.is_file():
        typer.echo(f"File not found: {p}", err=True)
        raise typer.Exit(1)

    result = run_ocr(p)

    if json_output:
        typer.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    typer.echo(f"  OCR            {'available' if result.ocr_available else 'not available'}")
    typer.echo(f"  Regions        {len(result.regions)}")
    if result.full_text:
        typer.echo(f"  Text           {result.full_text}")
    for limitation in result.limitations:
        typer.echo(f"  Limitation     {limitation}")
    typer.echo(f"  Schema         {result.schema}")
