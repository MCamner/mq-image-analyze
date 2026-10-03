"""CLI command: regress — visual regression of screenshots against a baseline."""
from __future__ import annotations

import dataclasses
import html
import json
import os
import shutil
from pathlib import Path

import typer
from PIL import Image, ImageDraw


def regress_cmd(
    baseline: Path = typer.Argument(..., help="Directory of approved screenshots", exists=True, file_okay=False),
    current: Path = typer.Argument(..., help="Directory of new screenshots, same file names", exists=True, file_okay=False),
    fail_over: float = typer.Option(
        0.0,
        "--fail-over",
        min=0.0,
        max=1.0,
        help="Fail a screen when its share of changed pixels exceeds this (0-1). Default 0: any real change.",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help="Write report.jsonl, report.html, overlays/ and one perception.v1 artifact per failing screen. "
        "Use reports/perception/<name> for mq-mcp Release Gate to pick the artifacts up.",
    ),
    source_type: str = typer.Option(
        "screenshot", "--source-type", help="perception.v1 source_type: screenshot | ui | browser | terminal"
    ),
    ignore_region: list[str] = typer.Option(
        [],
        "--ignore-region",
        help="Exclude a box from comparison: x1,y1,x2,y2 (baseline pixels) for every screen, "
        "or name.png:x1,y1,x2,y2 for one. Repeatable.",
    ),
    fail_on: str = typer.Option(
        "any",
        "--fail-on",
        help="any: every changed screen fails. text: only text changes (read with OCR), size changes and "
        "missing screens fail; without OCR every changed screen fails.",
    ),
    text: bool = typer.Option(True, "--text/--no-text", help="Read text in changed regions with OCR."),
    json_output: bool = typer.Option(False, "--json", help="Print JSONL, one line per screen."),
    update_baseline: bool = typer.Option(
        False,
        "--update-baseline",
        help="Copy every current screenshot into the baseline (new and changed), then exit 0. "
        "Nothing is deleted from the baseline.",
    ),
) -> None:
    """Compare a directory of screenshots against a baseline. Exit 1 if a screen changed or disappeared."""
    from mq_image_analyze import perception
    from mq_image_analyze.reasoning.comparison.regress import FAIL_ON, parse_ignore, regress

    if fail_on not in FAIL_ON:
        typer.echo(f"Error: --fail-on must be one of {list(FAIL_ON)}", err=True)
        raise typer.Exit(2)
    if source_type not in perception.SOURCE_TYPES:
        typer.echo(f"Error: --source-type must be one of {sorted(perception.SOURCE_TYPES)}", err=True)
        raise typer.Exit(2)

    try:
        ignore = parse_ignore(ignore_region)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(2) from exc

    report = regress(baseline, current, fail_over=fail_over, ignore=ignore, text=text, fail_on=fail_on)

    if update_baseline:
        copied = [e for e in report.entries if e.status in ("new", "changed", "unchanged") and e.current]
        for entry in copied:
            shutil.copy2(entry.current, baseline / entry.name)
        typer.echo(f"Updated baseline: {len(copied)} screenshot(s) copied into {baseline}")
        return

    lines = [json.dumps(dataclasses.asdict(e)) for e in report.entries]
    if json_output:
        for line in lines:
            typer.echo(line)
    else:
        for e in report.entries:
            detail = f"changed {e.changed_ratio:.4%}, {len(e.regions)} region(s)" if e.changed_ratio is not None else ""
            label = e.status.upper() if e.failed or e.status != "changed" else "CHANGED*"
            typer.echo(f"  {label:9}  {e.name}  {detail}".rstrip())
            for change in e.text_changes:
                if change["kind"] == "changed":
                    typer.echo(f"             text changed: {change['before']!r} → {change['after']!r}")
                elif change["kind"] == "added":
                    typer.echo(f"             text added:   {change['after']!r}")
                elif change["kind"] == "removed":
                    typer.echo(f"             text removed: {change['before']!r}")
            if e.text_ocr == "unavailable":
                typer.echo("             text not read: OCR unavailable")
        typer.echo(
            f"\n{len(report.entries)} screen(s), {report.failed} failed (--fail-over {fail_over}, --fail-on {fail_on})"
        )
        if any(e.status == "changed" and not e.failed for e in report.entries):
            typer.echo("CHANGED* = pixels changed, no text change: passes with --fail-on text")

    if out is not None:
        _write_outputs(out, report, lines, source_type)
        if not json_output:
            typer.echo(f"Wrote {out}")

    if report.failed:
        raise typer.Exit(1)


def _write_outputs(out: Path, report, lines: list[str], source_type: str) -> None:
    from mq_image_analyze import perception

    (out / "overlays").mkdir(parents=True, exist_ok=True)
    (out / "report.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for entry in report.entries:
        if entry.failed:
            record = perception.from_regression(entry, fail_over=report.fail_over, source_type=source_type)
            (out / f"{entry.name}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if entry.status == "changed":
            _overlay(entry, out / "overlays" / entry.name)
    (out / "report.html").write_text(_html(out, report), encoding="utf-8")


def _overlay(entry, target: Path) -> None:
    """The current screen, at baseline size, with changed regions outlined."""
    with Image.open(entry.baseline) as b, Image.open(entry.current) as c:
        img = c.convert("RGB").resize(b.size) if c.size != b.size else c.convert("RGB")
    draw = ImageDraw.Draw(img)
    for box in entry.ignored_regions:
        draw.rectangle(box, fill=(128, 128, 128))
    for region in entry.regions:
        draw.rectangle(region["bbox"], outline=(255, 64, 64), width=3)
    img.save(target)


def _html(out: Path, report) -> str:
    def rel(path: str | Path) -> str:
        return html.escape(os.path.relpath(path, out))

    rows = []
    for e in report.entries:
        if e.status == "unchanged":
            continue
        left = f'<img src="{rel(e.baseline)}" alt="baseline">' if e.baseline else "<em>none</em>"
        if e.status == "changed":
            right = f'<img src="{rel(out / "overlays" / e.name)}" alt="current with changes outlined">'
        elif e.current:
            right = f'<img src="{rel(e.current)}" alt="current">'
        else:
            right = "<em>missing</em>"
        detail = f"changed {e.changed_ratio:.4%} · {len(e.regions)} region(s)" if e.changed_ratio is not None else ""
        for change in e.text_changes:
            if change["kind"] != "visual":
                detail += (
                    f"<br>text {change['kind']}: <q>{html.escape(change['before'])}</q> → "
                    f"<q>{html.escape(change['after'])}</q>"
                )
        rows.append(
            f'<section class="{e.status}"><h2>{html.escape(e.name)} <span>{e.status}</span></h2>'
            f"<p>{detail}</p><div class=\"pair\"><figure>{left}<figcaption>baseline</figcaption></figure>"
            f"<figure>{right}<figcaption>current</figcaption></figure></div></section>"
        )
    unchanged = sum(e.status == "unchanged" for e in report.entries)
    body = "\n".join(rows) or "<p>No changed, missing or new screens.</p>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visual regression</title>
<style>
:root {{ --bg:#0d0b07; --fg:#f2d9a4; --dim:#a08a5c; --line:#3a2f1c; --bad:#ff6b4a; --new:#7fc8f8; }}
body {{ margin:0; padding:16px; background:var(--bg); color:var(--fg); font-family:"JetBrains Mono",ui-monospace,monospace; }}
h1 {{ font-size:1.2rem; }} h2 {{ font-size:1rem; margin:0; }} h2 span {{ color:var(--dim); font-weight:normal; }}
section {{ border:1px solid var(--line); padding:12px; margin:12px 0; }}
section.changed h2 span, section.missing h2 span {{ color:var(--bad); }} section.new h2 span {{ color:var(--new); }}
.pair {{ display:flex; flex-wrap:wrap; gap:12px; }} figure {{ margin:0; flex:1 1 280px; min-width:0; }}
img {{ max-width:100%; border:1px solid var(--line); }} figcaption, p {{ color:var(--dim); font-size:.85rem; }}
</style></head><body>
<h1>Visual regression — {report.failed} failed, {unchanged} unchanged, fail-over {report.fail_over}</h1>
{body}
</body></html>
"""
