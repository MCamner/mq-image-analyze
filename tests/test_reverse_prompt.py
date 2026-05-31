from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult, build

HEX = re.compile(r"^#[0-9a-f]{6}$")


def test_build_returns_result(dark_image: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=["person"]):
        result = build(dark_image)
    assert isinstance(result, ReversePromptResult)


def test_build_palette_is_hex_list(dark_image: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=[]):
        result = build(dark_image)
    for c in result.palette:
        assert HEX.match(c), f"{c!r} is not a valid hex color"


def test_build_prompt_is_nonempty_string(dark_image: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=["monitor"]):
        result = build(dark_image)
    assert isinstance(result.prompt, str)
    assert len(result.prompt) > 0


def test_build_includes_brightness(dark_image: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=[]):
        result = build(dark_image)
    assert result.brightness == "dark"
    # prompt is AI-generated (bakllava) — assert non-empty, not exact keyword presence
    assert isinstance(result.prompt, str)
    assert len(result.prompt) > 0


def test_build_includes_detected_objects(dark_image: Path) -> None:
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.detect_labels", return_value=["monitor", "keyboard"]):
        result = build(dark_image)
    assert "monitor" in result.objects
    assert "keyboard" in result.objects
