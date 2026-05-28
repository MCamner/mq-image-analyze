"""CLI command: observe-architecture — produce visual_architecture_observation.v1 JSON."""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import typer


def observe_architecture_cmd(
    image_path: str = typer.Argument(..., help="Path to architecture diagram or screenshot."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Observe an architecture diagram and return visual_architecture_observation.v1 JSON."""
    from mq_image_analyze.pipelines.architecture_pipeline import observe_architecture

    p = Path(image_path).expanduser().resolve()
    if not p.exists():
        typer.echo(f"File not found: {p}", err=True)
        raise typer.Exit(1)

    result = observe_architecture(p)
    d = dataclasses.asdict(result)

    if json_output:
        typer.echo(json.dumps(d, indent=2))
        return

    # Human-readable summary
    typer.echo(f"  Image type     {result.image_type}")
    typer.echo(f"  Components     {result.layout.component_count}")
    typer.echo(f"  Connections    {result.layout.connection_count}")
    typer.echo(f"  Groups         {len(result.groups)}")
    typer.echo(f"  Flow           {result.layout.dominant_flow}")
    typer.echo(f"  OCR            {'available' if result.ocr_available else 'not available'}")
    if result.limitations:
        typer.echo(f"  Limitations    {result.limitations[0][:80]}")
    typer.echo(f"  Schema         {result.schema_version}")
