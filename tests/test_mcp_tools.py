from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    from PIL import Image
    img = Image.new("RGB", (120, 120), color=(80, 120, 160))
    p = tmp_path / "sample.jpg"
    img.save(p)
    return p


@pytest.fixture
def dark_image(tmp_path: Path) -> Path:
    from PIL import Image
    img = Image.new("RGB", (120, 120), color=(20, 20, 20))
    p = tmp_path / "dark.jpg"
    img.save(p)
    return p


# ── analyze_image ─────────────────────────────────────────────────────────────

def test_analyze_image_returns_json(sample_image: Path):
    from mq_image_analyze.mcp.server import analyze_image
    raw = analyze_image(str(sample_image))
    d = json.loads(raw)
    assert "prompt" in d
    assert "objects" in d
    assert "palette" in d
    assert "limitations" in d
    assert "content_flags" in d


def test_analyze_image_missing_file():
    from mq_image_analyze.mcp.server import analyze_image
    with pytest.raises(FileNotFoundError):
        analyze_image("/nonexistent/image.jpg")


def test_analyze_image_bad_extension(tmp_path: Path):
    from mq_image_analyze.mcp.server import analyze_image
    p = tmp_path / "file.txt"
    p.write_text("not an image")
    with pytest.raises(ValueError, match="Unsupported image format"):
        analyze_image(str(p))


# ── extract_palette ───────────────────────────────────────────────────────────

def test_extract_palette_returns_json(sample_image: Path):
    from mq_image_analyze.mcp.server import extract_palette
    raw = extract_palette(str(sample_image))
    d = json.loads(raw)
    assert "palette" in d
    assert "brightness" in d
    assert "contrast" in d
    assert isinstance(d["palette"], list)
    assert all(c.startswith("#") for c in d["palette"])


# ── reverse_prompt ────────────────────────────────────────────────────────────

def test_reverse_prompt_returns_json(sample_image: Path):
    from mq_image_analyze.mcp.server import reverse_prompt
    raw = reverse_prompt(str(sample_image))
    d = json.loads(raw)
    assert "prompt" in d
    assert "objects" in d
    assert "palette" in d
    assert "limitations" in d
    assert isinstance(d["prompt"], str)


# ── compare_images ────────────────────────────────────────────────────────────

def test_compare_images_same(sample_image: Path):
    from mq_image_analyze.mcp.server import compare_images
    raw = compare_images(str(sample_image), str(sample_image))
    d = json.loads(raw)
    assert "palette_drift" in d
    assert "style_drift" in d
    assert "ai_look" in d
    assert d["palette_drift"] == 0.0


def test_compare_images_different(sample_image: Path, dark_image: Path):
    from mq_image_analyze.mcp.server import compare_images
    raw = compare_images(str(sample_image), str(dark_image))
    d = json.loads(raw)
    assert d["brightness_changed"] is True


# ── analyze_ui ────────────────────────────────────────────────────────────────

def test_analyze_ui_returns_json(sample_image: Path):
    from mq_image_analyze.mcp.server import analyze_ui
    raw = analyze_ui(str(sample_image))
    d = json.loads(raw)
    assert "screenshot_type" in d
    assert "contrast_ratio" in d
    assert "issues" in d
    assert "limitations" in d


# ── safety classification ─────────────────────────────────────────────────────

def test_safety_constant():
    from mq_image_analyze.mcp.server import _SAFETY
    assert _SAFETY == "safe"


def test_allowed_extensions():
    from mq_image_analyze.mcp.server import _ALLOWED_EXTENSIONS
    assert ".jpg" in _ALLOWED_EXTENSIONS
    assert ".png" in _ALLOWED_EXTENSIONS
    assert ".txt" not in _ALLOWED_EXTENSIONS
