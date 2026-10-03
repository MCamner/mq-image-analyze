"""mq-image regress: baseline screenshots against current ones.

Pairs by file name, measures pixel_diff and where the change is, and fails
the run when a screen changed more than --fail-over or disappeared. Failing
screens become perception.v1 artifacts for mq-mcp's Release Gate review.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from typer.testing import CliRunner

from mq_image_analyze import perception
from mq_image_analyze.cli import app
from mq_image_analyze.reasoning.comparison.regress import changed_regions, regress

runner = CliRunner()


def _screen(path: Path, *, box=None, size=(200, 100)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, "white")
    if box:
        ImageDraw.Draw(img).rectangle(box, fill="black")
    img.save(path)
    return path


@pytest.fixture
def dirs(tmp_path: Path) -> tuple[Path, Path]:
    base, cur = tmp_path / "baseline", tmp_path / "current"
    _screen(base / "home.png")
    _screen(cur / "home.png")                              # unchanged
    _screen(base / "login.png")
    _screen(cur / "login.png", box=(20, 20, 79, 59))       # changed
    _screen(base / "settings.png")                         # missing in current
    _screen(cur / "about.png")                             # new
    return base, cur


# ── regions ──────────────────────────────────────────────────────────────────

def test_identical_images_have_no_regions(tmp_path: Path):
    a = _screen(tmp_path / "a.png")
    assert changed_regions(a, a) == []


def test_a_changed_area_is_located(tmp_path: Path):
    a = _screen(tmp_path / "a.png")
    b = _screen(tmp_path / "b.png", box=(20, 20, 79, 59))
    regions = changed_regions(a, b)
    assert len(regions) == 1
    x1, y1, x2, y2 = regions[0]["bbox"]
    assert x1 <= 20 and y1 <= 20 and x2 >= 79 and y2 >= 59
    assert x2 - x1 < 80 and y2 - y1 < 60
    assert regions[0]["area_percent"] > 0


# ── pairing and status ───────────────────────────────────────────────────────

def test_statuses(dirs):
    report = regress(*dirs, fail_over=0.01)
    status = {e.name: e.status for e in report.entries}
    assert status == {"about.png": "new", "home.png": "unchanged", "login.png": "changed", "settings.png": "missing"}
    assert [e.name for e in report.entries] == sorted(status)
    assert report.failed == 2


def test_threshold_decides_changed(dirs):
    report = regress(*dirs, fail_over=0.5)
    login = next(e for e in report.entries if e.name == "login.png")
    assert login.status == "unchanged"
    assert 0 < login.changed_ratio < 0.5


def test_a_small_label_change_fails_at_the_default_threshold(tmp_path: Path):
    """A renamed button barely moves the mean (pixel_diff ~0.001), so the
    threshold must apply to the share of changed pixels, and default to any
    change that survives noise filtering."""
    base, cur = tmp_path / "b", tmp_path / "c"
    _screen(base / "s.png", size=(640, 400))
    _screen(cur / "s.png", box=(40, 280, 52, 300), size=(640, 400))  # 13x21 px
    entry = regress(base, cur, fail_over=0.0).entries[0]
    assert entry.pixel_diff < 0.01
    assert entry.status == "changed"


def test_noise_below_the_pixel_threshold_is_unchanged(tmp_path: Path):
    base, cur = tmp_path / "b", tmp_path / "c"
    _screen(base / "s.png")
    cur.mkdir()
    Image.new("RGB", (200, 100), (250, 250, 250)).save(cur / "s.png")  # off-white: below PIXEL_THRESHOLD
    entry = regress(base, cur, fail_over=0.0).entries[0]
    assert entry.pixel_diff > 0
    assert entry.status == "unchanged"
    assert entry.regions == []


# ── perception artifact ──────────────────────────────────────────────────────

def test_a_changed_screen_becomes_a_perception_record(dirs):
    report = regress(*dirs, fail_over=0.01)
    login = next(e for e in report.entries if e.name == "login.png")
    record = perception.from_regression(login, fail_over=0.01, source_type="screenshot")
    assert record["schema_version"] == perception.SCHEMA_VERSION
    assert record["source_type"] == "screenshot"
    assert record["source_path"].endswith("login.png")
    assert record["detected_regions"]
    assert any("changed_ratio" in s for s in record["risk_signals"])
    assert record["confidence"] in perception.CONFIDENCE_LEVELS


def test_a_missing_screen_becomes_a_perception_record(dirs):
    report = regress(*dirs, fail_over=0.01)
    missing = next(e for e in report.entries if e.name == "settings.png")
    record = perception.from_regression(missing, fail_over=0.01, source_type="ui")
    assert any("missing" in s for s in record["risk_signals"])
    assert record["source_path"].endswith("settings.png")


# ── CLI ──────────────────────────────────────────────────────────────────────

def test_cli_fails_and_writes_artifacts(dirs, tmp_path: Path):
    out = tmp_path / "reports" / "perception" / "regress"
    result = runner.invoke(app, ["regress", *map(str, dirs), "--out", str(out)])
    assert result.exit_code == 1, result.output
    lines = [json.loads(line) for line in (out / "report.jsonl").read_text().splitlines()]
    assert {line["name"] for line in lines} == {"about.png", "home.png", "login.png", "settings.png"}
    artifacts = sorted(p.name for p in out.glob("*.json"))
    assert artifacts == ["login.png.json", "settings.png.json"]
    html = (out / "report.html").read_text()
    assert "login.png" in html and "settings.png" in html
    assert (out / "overlays" / "login.png").is_file()


def test_cli_default_threshold_is_any_change(dirs):
    result = runner.invoke(app, ["regress", *map(str, dirs), "--json"])
    login = next(json.loads(line) for line in result.stdout.splitlines() if '"login.png"' in line)
    assert login["status"] == "changed"


def test_cli_passes_when_within_threshold(tmp_path: Path):
    base, cur = tmp_path / "b", tmp_path / "c"
    _screen(base / "home.png")
    _screen(cur / "home.png")
    result = runner.invoke(app, ["regress", str(base), str(cur)])
    assert result.exit_code == 0, result.output
    assert "0 failed" in result.output


def test_cli_json_is_jsonl_on_stdout(dirs):
    result = runner.invoke(app, ["regress", *map(str, dirs), "--json"])
    assert result.exit_code == 1
    names = [json.loads(line)["name"] for line in result.stdout.strip().splitlines()]
    assert names == ["about.png", "home.png", "login.png", "settings.png"]


def test_cli_update_baseline_copies_current_and_passes(dirs):
    base, cur = dirs
    result = runner.invoke(app, ["regress", str(base), str(cur), "--update-baseline"])
    assert result.exit_code == 0, result.output
    assert (base / "about.png").is_file()
    assert (base / "login.png").read_bytes() == (cur / "login.png").read_bytes()
    assert (base / "settings.png").is_file(), "a screen missing from current is not deleted from baseline"
    assert regress(base, cur, fail_over=0.01).failed == 1  # only settings.png, still missing


def test_cli_rejects_a_missing_directory(tmp_path: Path):
    result = runner.invoke(app, ["regress", str(tmp_path / "nope"), str(tmp_path)])
    assert result.exit_code != 0
