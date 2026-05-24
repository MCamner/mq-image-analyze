from __future__ import annotations

from pathlib import Path

from mq_image_analyze.vision.composition.analyzer import (
    depth_label,
    rule_of_thirds_score,
    symmetry_score,
    visual_weight,
)


def test_symmetry_score_range(symmetric_image: Path) -> None:
    score = symmetry_score(symmetric_image)
    assert 0.0 <= score <= 1.0


def test_symmetry_high_for_symmetric(symmetric_image: Path) -> None:
    assert symmetry_score(symmetric_image) > 0.8


def test_rule_of_thirds_range(dark_image: Path) -> None:
    score = rule_of_thirds_score(dark_image)
    assert 0.0 <= score <= 1.0


def test_visual_weight_returns_string(dark_image: Path) -> None:
    result = visual_weight(dark_image)
    assert result in {"left-heavy", "right-heavy", "centered", "balanced"}


def test_depth_label_returns_string(dark_image: Path) -> None:
    result = depth_label(dark_image)
    assert isinstance(result, str)
    assert len(result) > 0
