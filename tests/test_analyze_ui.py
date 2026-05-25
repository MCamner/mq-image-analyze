from __future__ import annotations

import dataclasses
from pathlib import Path

import numpy as np
import pytest

from mq_image_analyze.vision.ui.analyzer import (
    UIAnalysisResult,
    _accessibility_issues,
    _color_scheme,
    _detect_screenshot_type,
    _text_density,
    _wcag_contrast,
    analyze_ui,
)


def _make_screenshot(tmp_path: Path, rgb: tuple, size: tuple = (400, 300)) -> Path:
    from PIL import Image
    img = Image.new("RGB", size, color=rgb)
    p = tmp_path / "screen.png"
    img.save(p)
    return p


def test_wcag_contrast_white_black():
    ratio = _wcag_contrast((255, 255, 255), (0, 0, 0))
    assert ratio == 21.0


def test_wcag_contrast_identical():
    assert _wcag_contrast((128, 128, 128), (128, 128, 128)) == 1.0


def test_wcag_contrast_symmetric():
    a = _wcag_contrast((255, 255, 255), (100, 100, 100))
    b = _wcag_contrast((100, 100, 100), (255, 255, 255))
    assert a == b


def test_color_scheme_dark():
    assert _color_scheme(0.1) == "dark"


def test_color_scheme_light():
    assert _color_scheme(0.85) == "light"


def test_color_scheme_mixed():
    assert _color_scheme(0.5) == "mixed"


def test_accessibility_issues_low_contrast():
    issues = _accessibility_issues(2.5, "high", "light")
    assert any("4.5" in i for i in issues)


def test_accessibility_issues_pass():
    issues = _accessibility_issues(7.0, "high", "light")
    assert issues == []


def test_analyze_ui_dark_screen(tmp_path: Path):
    p = _make_screenshot(tmp_path, (15, 15, 15), size=(800, 600))
    result = analyze_ui(p)
    assert isinstance(result, UIAnalysisResult)
    assert result.color_scheme == "dark"
    assert result.contrast_ratio >= 1.0
    assert isinstance(result.layout_regions, list)
    assert isinstance(result.issues, list)
    assert result.prompt != ""


def test_analyze_ui_light_screen(tmp_path: Path):
    p = _make_screenshot(tmp_path, (240, 240, 240), size=(800, 1200))
    result = analyze_ui(p)
    assert result.color_scheme == "light"


def test_analyze_ui_returns_serialisable(tmp_path: Path):
    p = _make_screenshot(tmp_path, (30, 30, 30))
    result = analyze_ui(p)
    d = dataclasses.asdict(result)
    assert "screenshot_type" in d
    assert "contrast_ratio" in d
    assert "hierarchy_depth" in d
    assert "layout_regions" in d
    assert "issues" in d
    assert "limitations" in d


def test_analyze_ui_limitations_present(tmp_path: Path):
    p = _make_screenshot(tmp_path, (200, 200, 200))
    result = analyze_ui(p)
    assert len(result.limitations) > 0
