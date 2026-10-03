"""Opt-in cache for semantic captions — the slow and, for cloud-verify, paid step.

Keyed on image content, vision mode, model, redaction and the prompt text, so
a changed image, backend or prompt is a miss. Only captions that exist are
stored; a backend that was down is retried next time.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from typer.testing import CliRunner

from mq_image_analyze.cli import app
from mq_image_analyze.reasoning.prompts.reverse_prompt import build

DESCRIBE = "mq_image_analyze.reasoning.prompts.reverse_prompt.semantic_describe"


@pytest.fixture(autouse=True)
def cache_dir(tmp_path: Path, monkeypatch) -> Path:
    d = tmp_path / "cache"
    monkeypatch.setenv("MQ_IMAGE_CACHE_DIR", str(d))
    return d


def _image(tmp_path: Path, color=(10, 10, 10), name="a.png") -> Path:
    path = tmp_path / name
    Image.new("RGB", (16, 16), color=color).save(path)
    return path


def test_second_call_is_served_from_cache(tmp_path: Path):
    img = _image(tmp_path)
    with patch(DESCRIBE, return_value=("a caption", "local-fast", "bakllava")) as describe:
        first = build(img, cache=True)
        second = build(img, cache=True)
    assert describe.call_count == 1
    assert first.semantic_caption == second.semantic_caption == "a caption"
    assert any("cache" in item for item in second.limitations)


def test_without_cache_flag_nothing_is_stored(tmp_path: Path, cache_dir: Path):
    img = _image(tmp_path)
    with patch(DESCRIBE, return_value=("a caption", "local-fast", "bakllava")) as describe:
        build(img)
        build(img)
    assert describe.call_count == 2
    assert not cache_dir.exists()


def test_same_content_under_another_name_hits(tmp_path: Path):
    a = _image(tmp_path, name="a.png")
    b = tmp_path / "copy.png"
    b.write_bytes(a.read_bytes())
    with patch(DESCRIBE, return_value=("c", "local-fast", "bakllava")) as describe:
        build(a, cache=True)
        build(b, cache=True)
    assert describe.call_count == 1


def test_different_model_misses(tmp_path: Path):
    img = _image(tmp_path)
    with patch(DESCRIBE, return_value=("c", "local-fast", "bakllava")) as describe:
        build(img, cache=True, vision_model="bakllava")
        build(img, cache=True, vision_model="llava")
    assert describe.call_count == 2


def test_missing_caption_is_not_cached(tmp_path: Path):
    img = _image(tmp_path)
    with patch(DESCRIBE, return_value=(None, "local-fast", "bakllava")) as describe:
        build(img, cache=True)
        build(img, cache=True)
    assert describe.call_count == 2


def test_cli_cache_flag(tmp_path: Path):
    img = _image(tmp_path)
    with patch(DESCRIBE, return_value=("c", "local-fast", "bakllava")) as describe:
        for _ in range(2):
            result = CliRunner().invoke(app, ["analyze", str(img), "--cache", "--json"])
            assert result.exit_code == 0, result.output
    assert describe.call_count == 1
