from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

_REQUIRED_PACKAGES = ["ultralytics", "PIL", "cv2", "typer", "rich"]
_MODEL_PATH = Path(__file__).parents[2] / "models" / "yolov8n.pt"
_OUTPUT_DIR = Path(__file__).parents[2] / "outputs"


def _check(label: str, ok: bool, detail: str = "") -> dict:
    return {"check": label, "ok": ok, "detail": detail}


def _run_checks() -> list[dict]:
    results = []

    # Python version
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 11)
    results.append(_check("Python >= 3.11", ok, f"{major}.{minor}.{sys.version_info[2]}"))

    # Package imports
    for pkg in _REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            results.append(_check(f"import {pkg}", True))
        except ImportError as e:
            results.append(_check(f"import {pkg}", False, str(e)))

    # Model file
    results.append(_check(
        "models/yolov8n.pt",
        _MODEL_PATH.exists(),
        str(_MODEL_PATH) if not _MODEL_PATH.exists() else f"{_MODEL_PATH.stat().st_size // 1024} KB",
    ))

    # Output dir writable
    _OUTPUT_DIR.mkdir(exist_ok=True)
    writable = os.access(_OUTPUT_DIR, os.W_OK)
    results.append(_check("outputs/ writable", writable, str(_OUTPUT_DIR)))

    return results


def doctor(
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
) -> None:
    """Check system readiness — dependencies, model files, permissions."""
    results = _run_checks()
    all_ok = all(r["ok"] for r in results)

    if json_output:
        typer.echo(json.dumps({"checks": results, "ok": all_ok}, indent=2))
        raise typer.Exit(0 if all_ok else 1)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Check", style="bold")
    table.add_column("Status", width=6)
    table.add_column("Detail")

    for r in results:
        status = "[green]ok[/green]" if r["ok"] else "[red]fail[/red]"
        table.add_row(r["check"], status, r["detail"])

    console.print(table)
    if not all_ok:
        raise typer.Exit(1)
