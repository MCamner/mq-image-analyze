from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mq_image_analyze.reasoning.prompts.reverse_prompt import build

console = Console()


def analyze(
    image: Path = typer.Argument(..., help="Path to image file", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    exhaustive: bool = typer.Option(False, "--exhaustive", help="High-recall mode: all detections, no collapsing"),
    conf: Optional[float] = typer.Option(None, "--conf", help="Detection confidence threshold (default: 0.25 summary, 0.05 exhaustive)"),
) -> None:
    """Analyze an image — objects, style, composition, reverse prompt."""
    mode = "exhaustive" if exhaustive else "summary"
    result = build(image, mode=mode, conf=conf)

    if json_output:
        import json
        import dataclasses
        typer.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    console.print(Panel(f"[bold cyan]{image.name}[/bold cyan]  [dim]{mode}[/dim]", expand=False))

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

    console.print(table)
    console.print()
    console.print("[bold]Reverse prompt:[/bold]")
    console.print(f"  [italic]{result.prompt}[/italic]")
    console.print()
    console.print("[dim]Limitations:[/dim]")
    for lim in result.limitations:
        console.print(f"  [dim]· {lim}[/dim]")
