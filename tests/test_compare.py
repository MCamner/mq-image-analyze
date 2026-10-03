from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from mq_image_analyze.reasoning.comparison.comparator import (
    CompareResult,
    _ai_look_score,
    _color_distance,
    _palette_drift,
    compare,
)
from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    try:
        from PIL import Image
        img = Image.new("RGB", (100, 100), color=(120, 80, 60))
        p = tmp_path / "img.jpg"
        img.save(p)
        return p
    except ImportError:
        pytest.skip("Pillow not available")


def test_color_distance_identical():
    assert _color_distance("#ff0000", "#ff0000") == 0.0


def test_color_distance_max():
    d = _color_distance("#000000", "#ffffff")
    assert 0.99 < d <= 1.0


def test_color_distance_partial():
    d = _color_distance("#ff0000", "#00ff00")
    assert 0.0 < d < 1.0


def test_palette_drift_identical():
    palette = ["#ff0000", "#00ff00", "#0000ff"]
    assert _palette_drift(palette, palette) == 0.0


def test_palette_drift_empty():
    assert _palette_drift([], ["#ff0000"]) == 1.0
    assert _palette_drift(["#ff0000"], []) == 1.0


def test_palette_drift_different():
    a = ["#000000"]
    b = ["#ffffff"]
    assert _palette_drift(a, b) > 0.9


def _make_result(**kwargs) -> ReversePromptResult:
    defaults = dict(
        objects=[], palette=[], brightness="medium", contrast="medium contrast",
        depth="shallow", composition="centered", symmetry=0.5, rule_of_thirds=0.3,
        prompt="", mode="summary",
    )
    defaults.update(kwargs)
    return ReversePromptResult(**defaults)


def test_ai_look_score_low():
    r = _make_result(objects=["person", "car", "dog"], symmetry=0.2, rule_of_thirds=0.1)
    assert _ai_look_score(r) < 0.3


def test_ai_look_score_high():
    r = _make_result(objects=[], symmetry=0.95, rule_of_thirds=0.9)
    assert _ai_look_score(r) > 0.7


def test_compare_same_image(sample_image: Path):
    result = compare(sample_image, sample_image)
    assert isinstance(result, CompareResult)
    assert result.palette_drift == 0.0
    assert result.brightness_changed is False
    assert result.contrast_changed is False
    assert result.objects_added == []
    assert result.objects_removed == []
    assert result.composition_diff["symmetry_delta"] == 0.0


def test_compare_returns_serialisable(sample_image: Path):
    result = compare(sample_image, sample_image)
    d = dataclasses.asdict(result)
    assert "palette_drift" in d
    assert "style_drift" in d
    assert "ai_look" in d
    assert "before_result" in d
    assert "after_result" in d


# ── pixel_diff and --fail-over ───────────────────────────────────────────────

from PIL import Image as _Image  # noqa: E402
from typer.testing import CliRunner  # noqa: E402

from mq_image_analyze.cli import app  # noqa: E402
from mq_image_analyze.reasoning.comparison.comparator import _pixel_diff  # noqa: E402


def _png(path: Path, color, size=(40, 40)) -> Path:
    _Image.new("RGB", size, color=color).save(path)
    return path


def test_pixel_diff_identical_is_zero(tmp_path: Path):
    a = _png(tmp_path / "a.png", (10, 20, 30))
    assert _pixel_diff(a, a) == (0.0, False)


def test_pixel_diff_black_to_white_is_one(tmp_path: Path):
    a = _png(tmp_path / "a.png", (0, 0, 0))
    b = _png(tmp_path / "b.png", (255, 255, 255))
    assert _pixel_diff(a, b) == (1.0, False)


def test_pixel_diff_reports_size_change(tmp_path: Path):
    a = _png(tmp_path / "a.png", (0, 0, 0), size=(40, 40))
    b = _png(tmp_path / "b.png", (0, 0, 0), size=(80, 40))
    diff, size_changed = _pixel_diff(a, b)
    assert size_changed is True
    assert diff == 0.0


def test_compare_result_carries_pixel_diff(sample_image: Path):
    result = compare(sample_image, sample_image)
    assert result.pixel_diff == 0.0
    assert result.size_changed is False


def test_cli_fail_over_exits_1_when_exceeded(tmp_path: Path):
    a = _png(tmp_path / "a.png", (0, 0, 0))
    b = _png(tmp_path / "b.png", (255, 255, 255))
    result = CliRunner().invoke(app, ["compare", str(a), str(b), "--json", "--fail-over", "0.5"])
    assert result.exit_code == 1
    assert "pixel_diff" in result.output


def test_cli_fail_over_passes_under_threshold(tmp_path: Path):
    a = _png(tmp_path / "a.png", (0, 0, 0))
    result = CliRunner().invoke(app, ["compare", str(a), str(a), "--fail-over", "0.01"])
    assert result.exit_code == 0, result.output
