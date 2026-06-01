"""Tests for image_ocr.v1 pipeline and MCP tool."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image


# ── fixtures ──────────────────────────────────────────────────────────────────

def _save(arr, path: Path) -> Path:
    Image.fromarray(arr.astype("uint8")).save(path)
    return path


@pytest.fixture()
def blank_image(tmp_path: Path) -> Path:
    arr = np.full((200, 400, 3), 255, dtype="uint8")
    return _save(arr, tmp_path / "blank.png")


# ── ocr_pipeline ──────────────────────────────────────────────────────────────

def test_run_ocr_returns_ocr_result(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import OcrResult, run_ocr
    result = run_ocr(blank_image)
    assert isinstance(result, OcrResult)


def test_run_ocr_schema_version(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    assert result.schema == "image_ocr.v1"


def test_run_ocr_safety_is_safe(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    assert result.safety == "safe"


def test_run_ocr_limitations_always_present(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    assert isinstance(result.limitations, list)
    assert len(result.limitations) > 0


def test_run_ocr_limitations_include_data_warning(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    assert any("data" in lim.lower() or "instruction" in lim.lower() for lim in result.limitations)


def test_run_ocr_degrades_without_pytesseract(blank_image: Path) -> None:
    """When pytesseract is absent, ocr_available=False and regions is empty."""
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "pytesseract":
            raise ImportError("mocked absence")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        from mq_image_analyze.pipelines import ocr_pipeline
        import importlib
        importlib.reload(ocr_pipeline)
        result = ocr_pipeline.run_ocr(blank_image)

    assert result.ocr_available is False
    assert result.regions == []
    assert any("pytesseract" in lim.lower() for lim in result.limitations)


def test_run_ocr_regions_are_list(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    assert isinstance(result.regions, list)


def test_run_ocr_full_text_is_string(blank_image: Path) -> None:
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    assert isinstance(result.full_text, str)


def test_run_ocr_is_dataclass_serializable(blank_image: Path) -> None:
    import dataclasses
    from mq_image_analyze.pipelines.ocr_pipeline import run_ocr
    result = run_ocr(blank_image)
    d = dataclasses.asdict(result)
    assert isinstance(d, dict)
    assert "schema" in d and "regions" in d and "limitations" in d


# ── MCP tool ──────────────────────────────────────────────────────────────────

def test_mcp_image_ocr_returns_json(blank_image: Path) -> None:
    from mq_image_analyze.mcp.server import image_ocr
    result = image_ocr(str(blank_image))
    data = json.loads(result)
    assert data["schema"] == "image_ocr.v1"
    assert "regions" in data
    assert "limitations" in data
    assert data["safety"] == "safe"


def test_mcp_image_ocr_missing_file_raises() -> None:
    from mq_image_analyze.mcp.server import image_ocr
    with pytest.raises(FileNotFoundError):
        image_ocr("/nonexistent/path/image.png")


def test_mcp_image_ocr_unsupported_format(tmp_path: Path) -> None:
    bad = tmp_path / "file.txt"
    bad.write_text("not an image")
    from mq_image_analyze.mcp.server import image_ocr
    with pytest.raises(ValueError, match="Unsupported image format"):
        image_ocr(str(bad))
