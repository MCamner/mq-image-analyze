from __future__ import annotations

import re
from pathlib import Path

from mq_image_analyze.vision.palette.extractor import (
    brightness_label,
    contrast_label,
    extract,
)

HEX = re.compile(r"^#[0-9a-f]{6}$")


def test_extract_returns_hex_strings(two_color_image: Path) -> None:
    colors = extract(two_color_image, n_colors=2)
    assert len(colors) == 2
    for c in colors:
        assert HEX.match(c), f"{c!r} is not a valid hex color"


def test_extract_n_colors(dark_image: Path) -> None:
    colors = extract(dark_image, n_colors=4)
    assert len(colors) == 4


def test_brightness_dark(dark_image: Path) -> None:
    assert brightness_label(dark_image) == "dark"


def test_brightness_bright(bright_image: Path) -> None:
    assert brightness_label(bright_image) == "bright"


def test_contrast_low(dark_image: Path) -> None:
    assert contrast_label(dark_image) == "low contrast"
