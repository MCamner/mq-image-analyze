from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mq_image_analyze.formats import IMAGE_EXTENSIONS
from mq_image_analyze.reasoning.prompts.reverse_prompt import build
from mq_image_analyze.vision.semantic.provider import normalize_vision_mode

console = Console()


def analyze(
    image: Path = typer.Argument(..., help="Path to image file, or a directory of images (non-recursive)", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    exhaustive: bool = typer.Option(False, "--exhaustive", help="High-recall mode: all detections, no collapsing"),
    conf: Optional[float] = typer.Option(None, "--conf", help="Detection confidence threshold (default: 0.25 summary, 0.05 exhaustive)"),
    vision_mode: str = typer.Option(
        "local-fast",
        "--mode",
        help="Vision backend: local-fast, local-deep, or cloud-verify",
    ),
    vision_model: Optional[str] = typer.Option(
        None,
        "--vision-model",
        help="Override backend model, e.g. bakllava, llama3.2-vision, gpt-4o, gpt-4.1",
    ),
    redact: bool = typer.Option(
        False,
        "--redact",
        help="cloud-verify only: mask personnummer and emails found by OCR before upload; "
        "if OCR is unavailable the image is not sent. Also on with MQ_IMAGE_REDACT_CLOUD=1.",
    ),
) -> None:
    """Analyze an image — objects, style, composition, reverse prompt."""
    mode = "exhaustive" if exhaustive else "summary"
    try:
        selected_vision_mode = normalize_vision_mode(vision_mode)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc

    if image.is_dir():
        _analyze_dir(image, json_output, mode=mode, conf=conf, vision_mode=selected_vision_mode,
                     vision_model=vision_model, redact=redact)
        return

    result = build(
        image,
        mode=mode,
        conf=conf,
        vision_mode=selected_vision_mode,
        vision_model=vision_model,
        redact=redact,
    )

    if json_output:
        import json
        import dataclasses
        typer.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    console.print(
        Panel(
            f"[bold cyan]{image.name}[/bold cyan]  [dim]{mode} · {result.vision_mode} · {result.vision_model}[/dim]",
            expand=False,
        )
    )

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold green", width=22)
    table.add_column()

    if exhaustive and result.detections:
        det_lines = [
            f"{d['label']} ({d['confidence']:.2f}, {d['area_percent']}%)"
            for d in result.detections[:10]
        ]
        if len(result.detections) > 10:
            det_lines.append(f"... +{len(result.detections) - 10} more")
        table.add_row("Detections", "\n".join(det_lines))
    else:
        table.add_row("Objects", ", ".join(result.objects) or "none detected")

    table.add_row("Palette", " ".join(result.palette[:5]))
    table.add_row("Brightness", result.brightness)
    table.add_row("Contrast", result.contrast)
    table.add_row("Depth", result.depth)
    table.add_row("Composition", result.composition)
    table.add_row("Symmetry", str(result.symmetry))
    table.add_row("Rule of thirds", str(result.rule_of_thirds))
    table.add_row("Vision backend", f"{result.vision_mode} ({result.vision_model})")

    console.print(table)
    console.print()
    console.print("[bold]Reverse prompt:[/bold]")
    console.print(f"  [italic]{result.prompt}[/italic]")
    console.print()
    console.print("[dim]Limitations:[/dim]")
    for lim in result.limitations:
        console.print(f"  [dim]· {lim}[/dim]")


def _analyze_dir(directory: Path, json_output: bool, **build_kwargs) -> None:
    """Every image directly in `directory`, sorted by name. JSONL with --json.

    A failing image is reported on its own line and the batch continues;
    the exit code is 1 if any image failed.
    """
    import dataclasses
    import json

    images = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        typer.echo(f"No images in {directory}", err=True)
        raise typer.Exit(1)

    failed = 0
    for path in images:
        try:
            result = build(path, **build_kwargs)
        except Exception as exc:  # one broken file must not end the batch
            failed += 1
            if json_output:
                typer.echo(json.dumps({"path": str(path), "error": str(exc)}))
            else:
                console.print(f"[red]{path.name}[/red]  error: {exc}")
            continue
        if json_output:
            typer.echo(json.dumps({"path": str(path), **dataclasses.asdict(result)}))
        else:
            console.print(f"[bold cyan]{path.name}[/bold cyan]  [dim]{result.brightness} · {result.contrast}[/dim]")
            console.print(f"  [italic]{result.prompt}[/italic]")

    if not json_output:
        console.print(f"\n[dim]{len(images)} image(s), {failed} failed[/dim]")
    if failed:
        raise typer.Exit(1)
