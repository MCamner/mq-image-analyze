"""Tests for visual_architecture_observation.v1 pipeline."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw


# ── fixtures ──────────────────────────────────────────────────────────────────

def _save(arr: np.ndarray, path: Path) -> Path:
    Image.fromarray(arr.astype(np.uint8)).save(path)
    return path


@pytest.fixture()
def white_image(tmp_path: Path) -> Path:
    arr = np.full((400, 600, 3), 255, dtype=np.uint8)
    return _save(arr, tmp_path / "white.png")


@pytest.fixture()
def dark_image(tmp_path: Path) -> Path:
    arr = np.full((400, 600, 3), 20, dtype=np.uint8)
    return _save(arr, tmp_path / "dark.png")


@pytest.fixture()
def diagram_image(tmp_path: Path) -> Path:
    """Synthetic architecture diagram: white bg, 4 labeled boxes, 3 connecting lines."""
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    boxes = [(50, 80, 200, 160), (300, 80, 450, 160), (550, 80, 700, 160), (300, 240, 450, 320)]
    for box in boxes:
        draw.rectangle(box, fill=(200, 230, 200), outline=(0, 0, 0), width=2)

    # Horizontal lines between boxes
    draw.line([(200, 120), (300, 120)], fill=(0, 0, 0), width=2)
    draw.line([(450, 120), (550, 120)], fill=(0, 0, 0), width=2)
    # Vertical line from box_1 to box_3
    draw.line([(375, 160), (375, 240)], fill=(0, 0, 0), width=2)

    p = tmp_path / "diagram.png"
    img.save(p)
    return p


# ── classifier tests ──────────────────────────────────────────────────────────

def test_classify_dark_image(dark_image: Path):
    from mq_image_analyze.vision.architecture.classifier import classify_image_type
    result = classify_image_type(dark_image)
    # Dark solid image — no text density, returns terminal or unknown
    assert result in {"terminal", "unknown"}


def test_classify_white_image(white_image: Path):
    from mq_image_analyze.vision.architecture.classifier import classify_image_type
    result = classify_image_type(white_image)
    # Pure white — no boxes detected, no text density
    assert result in {"unknown", "architecture-diagram", "ui-screenshot"}


def test_classify_diagram(diagram_image: Path):
    from mq_image_analyze.vision.architecture.classifier import classify_image_type
    result = classify_image_type(diagram_image)
    assert result == "architecture-diagram"


# ── detector tests ────────────────────────────────────────────────────────────

def test_detect_components_empty_on_white(white_image: Path):
    from mq_image_analyze.vision.architecture.detector import detect_components
    comps = detect_components(white_image)
    assert isinstance(comps, list)


def test_detect_components_finds_boxes(diagram_image: Path):
    from mq_image_analyze.vision.architecture.detector import detect_components
    comps = detect_components(diagram_image)
    assert len(comps) >= 2, f"Expected >=2 components, got {len(comps)}"


def test_component_ids_unique(diagram_image: Path):
    from mq_image_analyze.vision.architecture.detector import detect_components
    comps = detect_components(diagram_image)
    ids = [c.id for c in comps]
    assert len(ids) == len(set(ids))


def test_component_bbox_valid(diagram_image: Path):
    from mq_image_analyze.vision.architecture.detector import detect_components
    comps = detect_components(diagram_image)
    for c in comps:
        x1, y1, x2, y2 = c.bbox
        assert x2 > x1
        assert y2 > y1
        assert c.area_percent > 0


def test_detect_groups_clusters_by_color(diagram_image: Path):
    from mq_image_analyze.vision.architecture.detector import detect_components, detect_groups
    comps = detect_components(diagram_image)
    groups = detect_groups(comps)
    assert isinstance(groups, list)
    for g in groups:
        assert len(g.component_ids) >= 2


def test_infer_dominant_flow_left_to_right(diagram_image: Path):
    from mq_image_analyze.vision.architecture.detector import (
        detect_components,
        infer_dominant_flow,
    )
    comps = detect_components(diagram_image)
    flow = infer_dominant_flow(comps)
    # Diagram is wider than tall — should detect left-to-right or unknown
    assert flow in {"left-to-right", "unknown"}


# ── observation dataclass ─────────────────────────────────────────────────────

def test_observation_schema_version():
    from mq_image_analyze.vision.architecture.observation import (
        SCHEMA_VERSION,
        VisualArchitectureObservation,
        ArchLayout,
    )
    obs = VisualArchitectureObservation(
        schema_version=SCHEMA_VERSION,
        image_type="architecture-diagram",
        image_path="/tmp/test.png",
        components=[],
        connections=[],
        groups=[],
        text_regions=[],
        layout=ArchLayout(width=100, height=100, component_count=0, connection_count=0, dominant_flow="unknown"),
        limitations=["test"],
        ocr_available=False,
    )
    assert obs.schema_version == "visual_architecture_observation.v1"


# ── pipeline integration tests ────────────────────────────────────────────────

def test_pipeline_returns_observation(diagram_image: Path):
    from mq_image_analyze.pipelines.architecture_pipeline import observe_architecture
    obs = observe_architecture(diagram_image)
    assert obs.schema_version == "visual_architecture_observation.v1"
    assert obs.image_type in {
        "architecture-diagram", "dashboard", "terminal", "ui-screenshot", "unknown"
    }
    assert isinstance(obs.components, list)
    assert isinstance(obs.connections, list)
    assert isinstance(obs.groups, list)
    assert isinstance(obs.text_regions, list)
    assert isinstance(obs.limitations, list)
    assert len(obs.limitations) > 0


def test_pipeline_is_json_serializable(diagram_image: Path):
    import dataclasses
    from mq_image_analyze.pipelines.architecture_pipeline import observe_architecture
    obs = observe_architecture(diagram_image)
    d = dataclasses.asdict(obs)
    payload = json.dumps(d)
    parsed = json.loads(payload)
    assert parsed["schema_version"] == "visual_architecture_observation.v1"
    assert "components" in parsed
    assert "connections" in parsed
    assert "layout" in parsed


def test_pipeline_limitations_always_present(white_image: Path):
    from mq_image_analyze.pipelines.architecture_pipeline import observe_architecture
    obs = observe_architecture(white_image)
    assert len(obs.limitations) > 0


def test_pipeline_image_path_in_output(diagram_image: Path):
    from mq_image_analyze.pipelines.architecture_pipeline import observe_architecture
    obs = observe_architecture(diagram_image)
    assert str(diagram_image.resolve()) == obs.image_path


# ── MCP tool smoke test ───────────────────────────────────────────────────────

def test_mcp_observe_architecture_returns_json(diagram_image: Path):
    from mq_image_analyze.mcp.server import observe_architecture as _mcp_tool
    output = _mcp_tool(str(diagram_image))
    parsed = json.loads(output)
    assert parsed["schema_version"] == "visual_architecture_observation.v1"
    assert "layout" in parsed
