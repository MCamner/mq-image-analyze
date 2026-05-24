from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mq_image_analyze.cli import app
from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult

runner = CliRunner()

HEX = re.compile(r"^#[0-9a-f]{6}$")

_MOCK = ReversePromptResult(
    objects=["person", "monitor"],
    palette=["#0a0a0f", "#1c1f2e", "#3a4a6b"],
    brightness="dark",
    contrast="moderate contrast",
    depth="shallow depth of field",
    composition="centered",
    symmetry=0.87,
    rule_of_thirds=0.45,
    prompt="person, monitor, dark scene",
)


def _analyze_json(tmp_path: Path) -> dict:
    import numpy as np
    from PIL import Image

    img = tmp_path / "t.jpg"
    Image.fromarray(__import__("numpy").zeros((50, 50, 3), dtype="uint8")).save(img)

    with patch("mq_image_analyze.cli.analyze.build", return_value=_MOCK):
        result = runner.invoke(app, ["analyze", str(img), "--json"])

    assert result.exit_code == 0
    return json.loads(result.output)


def test_schema_required_keys(tmp_path: Path) -> None:
    data = _analyze_json(tmp_path)
    required = {"objects", "palette", "brightness", "contrast", "depth", "composition", "symmetry", "rule_of_thirds", "prompt"}
    assert required <= data.keys()


def test_objects_is_list_of_strings(tmp_path: Path) -> None:
    data = _analyze_json(tmp_path)
    assert isinstance(data["objects"], list)
    assert all(isinstance(o, str) for o in data["objects"])


def test_palette_is_list_of_hex(tmp_path: Path) -> None:
    data = _analyze_json(tmp_path)
    assert isinstance(data["palette"], list)
    for color in data["palette"]:
        assert HEX.match(color), f"{color!r} is not a valid hex color"


def test_symmetry_is_float(tmp_path: Path) -> None:
    data = _analyze_json(tmp_path)
    assert isinstance(data["symmetry"], float)
    assert 0.0 <= data["symmetry"] <= 1.0


def test_prompt_is_string(tmp_path: Path) -> None:
    data = _analyze_json(tmp_path)
    assert isinstance(data["prompt"], str)
    assert len(data["prompt"]) > 0


def test_brightness_enum(tmp_path: Path) -> None:
    data = _analyze_json(tmp_path)
    assert data["brightness"] in {"dark", "mid-tone", "bright"}
