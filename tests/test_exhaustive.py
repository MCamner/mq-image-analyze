from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image
from typer.testing import CliRunner

from mq_image_analyze.cli import app
from mq_image_analyze.reasoning.prompts.reverse_prompt import build
from mq_image_analyze.vision.detection.detector import Detection

runner = CliRunner()


def _img(tmp_path: Path) -> Path:
    p = tmp_path / "t.jpg"
    Image.fromarray(np.zeros((50, 50, 3), dtype="uint8")).save(p)
    return p


_MULTI_PERSON = [
    Detection("person", 0.91, (10.0, 10.0, 100.0, 200.0), 12.4, "yolov8n"),
    Detection("person", 0.83, (200.0, 10.0, 290.0, 200.0), 11.2, "yolov8n"),
    Detection("monitor", 0.76, (300.0, 50.0, 450.0, 200.0), 9.1, "yolov8n"),
]


def test_exhaustive_preserves_duplicate_detections(tmp_path: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_all", return_value=_MULTI_PERSON):
        result = build(_img(tmp_path), mode="exhaustive")
    assert len(result.detections) == 3
    person_dets = [d for d in result.detections if d["label"] == "person"]
    assert len(person_dets) == 2, "exhaustive mode must not collapse duplicates"


def test_summary_collapses_duplicates(tmp_path: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=["person", "monitor"]):
        result = build(_img(tmp_path), mode="summary")
    assert result.detections == [], "summary mode must not include raw detections list"
    assert result.objects == ["person", "monitor"]


def test_exhaustive_includes_confidence_and_bbox(tmp_path: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_all", return_value=_MULTI_PERSON):
        result = build(_img(tmp_path), mode="exhaustive")
    first = result.detections[0]
    assert "confidence" in first
    assert "bbox" in first
    assert "area_percent" in first
    assert "source_model" in first


def test_exhaustive_json_has_detections_array(tmp_path: Path) -> None:
    img = _img(tmp_path)
    with patch("mq_image_analyze.cli.analyze.build") as mock_build:
        from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult
        mock_build.return_value = ReversePromptResult(
            objects=["person"],
            palette=["#000000"],
            brightness="dark",
            contrast="low contrast",
            depth="shallow depth of field",
            composition="balanced",
            symmetry=0.5,
            rule_of_thirds=0.3,
            prompt="person, dark scene",
            mode="exhaustive",
            detections=[{"label": "person", "confidence": 0.91, "bbox": [10, 10, 100, 200], "area_percent": 12.4, "source_model": "yolov8n"},
                        {"label": "person", "confidence": 0.83, "bbox": [200, 10, 290, 200], "area_percent": 11.2, "source_model": "yolov8n"}],
            limitations=["test limitation"],
        )
        result = runner.invoke(app, ["analyze", str(img), "--json", "--exhaustive"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["mode"] == "exhaustive"
    assert len(data["detections"]) == 2
    assert data["detections"][0]["label"] == "person"


def test_limitations_always_present(tmp_path: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=[]):
        result = build(_img(tmp_path), mode="summary")
    assert isinstance(result.limitations, list)
    assert len(result.limitations) > 0


def test_exhaustive_conf_defaults_to_005(tmp_path: Path) -> None:
    calls = []
    original = __import__("mq_image_analyze.vision.detection.detector", fromlist=["detect_all"]).detect_all

    def spy(path, conf=0.05):
        calls.append(conf)
        return []

    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_all", side_effect=spy):
        build(_img(tmp_path), mode="exhaustive")

    assert calls[0] == 0.05


def test_explicit_conf_overrides_default(tmp_path: Path) -> None:
    calls = []

    def spy(path, conf=0.05):
        calls.append(conf)
        return []

    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_all", side_effect=spy):
        build(_img(tmp_path), mode="exhaustive", conf=0.15)

    assert calls[0] == 0.15
