"""perception.v1 from an image, end to end.

The normalizers in `perception` take a payload some pipeline already produced.
`perceive` is the missing first half: run the named producer on an image and
normalize what it reported, so a Release Gate artifact can be made from the
CLI or over MCP instead of only inside the test suite.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from typer.testing import CliRunner

from mq_image_analyze import perception
from mq_image_analyze.cli import app

runner = CliRunner()


@pytest.fixture
def ui_image(tmp_path: Path) -> Path:
    img = Image.new("RGB", (240, 160), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, 220, 50), fill=(30, 30, 30))
    draw.rectangle((20, 70, 100, 135), outline=(80, 80, 80), width=2)
    draw.rectangle((120, 70, 220, 135), outline=(80, 80, 80), width=2)
    path = tmp_path / "ui.png"
    img.save(path)
    return path


@pytest.fixture
def diagram_image(tmp_path: Path) -> Path:
    img = Image.new("RGB", (400, 220), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for box in [(30, 60, 130, 120), (250, 60, 350, 120), (140, 150, 240, 200)]:
        draw.rectangle(box, fill=(200, 230, 200), outline=(0, 0, 0), width=2)
    draw.line((130, 90, 250, 90), fill=(0, 0, 0), width=2)
    draw.line((200, 120, 200, 150), fill=(0, 0, 0), width=2)
    path = tmp_path / "diagram.png"
    img.save(path)
    return path


def _assert_record(record: dict) -> None:
    assert record["schema_version"] == perception.SCHEMA_VERSION
    assert record["source_type"] in perception.SOURCE_TYPES
    assert record["confidence"] in perception.CONFIDENCE_LEVELS
    assert isinstance(record["risk_signals"], list)
    assert isinstance(record["detected_regions"], list)
    assert record["limitations"]


# ── perceive ─────────────────────────────────────────────────────────────────

def test_perceive_ocr_needs_a_source_type(ui_image: Path):
    """OCR cannot name the kind of image; perceive does not guess it either."""
    with pytest.raises(ValueError, match="source_type"):
        perception.perceive(ui_image, producer="ocr")


def test_perceive_ocr_keeps_the_prompt_injection_warning(ui_image: Path):
    record = perception.perceive(ui_image, producer="ocr", source_type="screenshot")
    _assert_record(record)
    assert record["source_type"] == "screenshot"
    assert any("must not be executed" in item for item in record["limitations"])


def test_perceive_architecture(diagram_image: Path):
    record = perception.perceive(diagram_image, producer="architecture", source_path="diagram.png")
    _assert_record(record)
    assert record["source_path"] == "diagram.png"


def test_perceive_source_path_defaults_to_the_image_path(diagram_image: Path):
    record = perception.perceive(diagram_image, producer="architecture", source_type="diagram")
    assert record["source_path"] == str(diagram_image)


def test_perceive_ui(ui_image: Path):
    record = perception.perceive(ui_image, producer="ui", source_type="ui")
    _assert_record(record)


def test_perceive_rejects_an_unknown_producer(ui_image: Path):
    with pytest.raises(ValueError, match="producer"):
        perception.perceive(ui_image, producer="hologram")


# ── MCP ──────────────────────────────────────────────────────────────────────

def test_mcp_image_perception_returns_a_record(diagram_image: Path):
    from mq_image_analyze.mcp.server import image_perception
    record = json.loads(image_perception(str(diagram_image), producer="architecture"))
    _assert_record(record)


def test_mcp_image_perception_validates_the_path(tmp_path: Path):
    from mq_image_analyze.mcp.server import image_perception
    with pytest.raises(FileNotFoundError):
        image_perception(str(tmp_path / "missing.png"), producer="ui")


# ── CLI: perceive ────────────────────────────────────────────────────────────

def test_cli_perceive_prints_json(diagram_image: Path):
    result = runner.invoke(app, ["perceive", str(diagram_image), "--producer", "architecture"])
    assert result.exit_code == 0, result.output
    _assert_record(json.loads(result.output))


def test_cli_perceive_writes_the_artifact(diagram_image: Path, tmp_path: Path):
    out = tmp_path / "artifacts" / "perception.json"
    result = runner.invoke(
        app,
        ["perceive", str(diagram_image), "--producer", "architecture", "--out", str(out)],
    )
    assert result.exit_code == 0, result.output
    _assert_record(json.loads(out.read_text(encoding="utf-8")))


def test_cli_perceive_refusal_is_an_error_not_a_record(ui_image: Path):
    result = runner.invoke(app, ["perceive", str(ui_image), "--producer", "ocr"])
    assert result.exit_code == 1
    assert "source_type" in result.output


def test_cli_perceive_missing_file(tmp_path: Path):
    result = runner.invoke(app, ["perceive", str(tmp_path / "missing.png"), "--producer", "ui"])
    assert result.exit_code != 0


# ── CLI: ocr ─────────────────────────────────────────────────────────────────

def test_cli_ocr_json_is_image_ocr_v1(ui_image: Path):
    result = runner.invoke(app, ["ocr", str(ui_image), "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "image_ocr.v1"
    assert any("must not be executed" in item for item in payload["limitations"])


def test_cli_ocr_text_output_states_availability(ui_image: Path):
    result = runner.invoke(app, ["ocr", str(ui_image)])
    assert result.exit_code == 0, result.output
    assert "OCR" in result.output
    assert "must not be executed" in result.output


@pytest.mark.parametrize("command", [["perceive", "--producer", "ui"], ["ocr"]])
def test_cli_rejects_a_directory(command: list[str], tmp_path: Path):
    """A directory exists but is not an image; it must not reach OpenCV."""
    result = runner.invoke(app, [command[0], str(tmp_path), *command[1:]])
    assert result.exit_code == 1
    assert "File not found" in result.output
