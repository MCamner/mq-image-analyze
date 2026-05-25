from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mq_image_analyze.reasoning.comparison.comparator import compare as run_compare

console = Console()


def compare(
    before: Path = typer.Argument(..., help="Before image", exists=True),
    after: Path = typer.Argument(..., help="After image", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    exhaustive: bool = typer.Option(False, "--exhaustive", help="Use exhaustive detection mode"),
    conf: Optional[float] = typer.Option(None, "--conf", help="Detection confidence threshold"),
) -> None:
    """Compare two images — palette drift, composition diff, style drift, AI-look score."""
    mode = "exhaustive" if exhaustive else "summary"
    result = run_compare(before, after, mode=mode, conf=conf)

    if json_output:
        typer.echo(json.dumps(dataclasses.asdict(result), indent=2))
        return

    console.print(Panel(
        f"[bold cyan]{before.name}[/bold cyan] [dim]→[/dim] [bold cyan]{after.name}[/bold cyan]",
        expand=False,
    ))

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold green", width=22)
    table.add_column()

    def drift_color(v: float) -> str:
        if v < 0.15:
            return f"[green]{v}[/green]"
        if v < 0.4:
            return f"[yellow]{v}[/yellow]"
        return f"[red]{v}[/red]"

    table.add_row("Palette drift",     drift_color(result.palette_drift))
    table.add_row("Style drift",       drift_color(result.style_drift))
    table.add_row("Brightness",        "[yellow]changed[/yellow]" if result.brightness_changed else "[green]same[/green]")
    table.add_row("Contrast",          "[yellow]changed[/yellow]" if result.contrast_changed else "[green]same[/green]")
    table.add_row("Depth",             "[yellow]changed[/yellow]" if result.depth_changed else "[green]same[/green]")
    table.add_row("Symmetry Δ",        str(result.composition_diff["symmetry_delta"]))
    table.add_row("Rule-of-thirds Δ",  str(result.composition_diff["rule_of_thirds_delta"]))

    if result.objects_added:
        table.add_row("Objects added",    ", ".join(result.objects_added))
    if result.objects_removed:
        table.add_row("Objects removed",  ", ".join(result.objects_removed))

    ai_b = result.ai_look["before"]
    ai_a = result.ai_look["after"]
    table.add_row("AI-look before",    f"{ai_b:.2f}")
    table.add_row("AI-look after",     f"{ai_a:.2f}")

    console.print(table)
    console.print()
    console.print("[bold]Before prompt:[/bold]")
    console.print(f"  [italic]{result.before_result['prompt']}[/italic]")
    console.print("[bold]After prompt:[/bold]")
    console.print(f"  [italic]{result.after_result['prompt']}[/italic]")
