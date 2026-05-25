from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mq_image_analyze.vision.ui.analyzer import analyze_ui

console = Console()


def analyze_ui_cmd(
    image: Path = typer.Argument(..., help="Path to screenshot", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Analyze a UI screenshot — layout, contrast, hierarchy, accessibility."""
    result = analyze_ui(image)

    if json_output:
        typer.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    console.print(Panel(
        f"[bold cyan]{image.name}[/bold cyan]  [dim]{result.screenshot_type}[/dim]",
        expand=False,
    ))

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold green", width=22)
    table.add_column()

    def contrast_color(v: float) -> str:
        if v >= 7.0:
            return f"[green]{v:.1f}:1 (AAA)[/green]"
        if v >= 4.5:
            return f"[green]{v:.1f}:1 (AA)[/green]"
        if v >= 3.0:
            return f"[yellow]{v:.1f}:1 (AA large)[/yellow]"
        return f"[red]{v:.1f}:1 (fail)[/red]"

    table.add_row("Type",           result.screenshot_type)
    table.add_row("Color scheme",   result.color_scheme)
    table.add_row("Text density",   result.text_density)
    table.add_row("Contrast ratio", contrast_color(result.contrast_ratio))
    table.add_row("Hierarchy depth", str(result.hierarchy_depth))
    table.add_row("Grid alignment", str(result.grid_alignment))

    if result.layout_regions:
        region_lines = [
            f"{r['role']} ({r['area_percent']}%)" for r in result.layout_regions[:5]
        ]
        table.add_row("Regions", "\n".join(region_lines))

    console.print(table)

    if result.issues:
        console.print()
        console.print("[bold red]Accessibility issues:[/bold red]")
        for issue in result.issues:
            console.print(f"  [red]· {issue}[/red]")
    else:
        console.print()
        console.print("[green]No accessibility issues detected.[/green]")

    console.print()
    if result.semantic_caption:
        console.print("[bold]Semantic description:[/bold]")
        console.print(f"  [italic]{result.semantic_caption}[/italic]")
        console.print()
    console.print("[bold]Prompt:[/bold]")
    console.print(f"  [italic]{result.prompt}[/italic]")
    console.print()
    console.print("[dim]Limitations:[/dim]")
    for lim in result.limitations:
        console.print(f"  [dim]· {lim}[/dim]")
