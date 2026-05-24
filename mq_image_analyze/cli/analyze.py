from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mq_image_analyze.reasoning.prompts.reverse_prompt import build

console = Console()


def analyze(
    image: Path = typer.Argument(..., help="Path to image file", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Analyze an image — objects, style, composition, reverse prompt."""
    result = build(image)

    if json_output:
        import json
        import dataclasses
        typer.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    console.print(Panel(f"[bold cyan]{image.name}[/bold cyan]", expand=False))

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold green", width=20)
    table.add_column()

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
