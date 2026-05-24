from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image


def _save(arr: np.ndarray, path: Path) -> Path:
    Image.fromarray(arr.astype(np.uint8)).save(path)
    return path


@pytest.fixture()
def dark_image(tmp_path: Path) -> Path:
    arr = np.full((100, 100, 3), 20)
    return _save(arr, tmp_path / "dark.jpg")


@pytest.fixture()
def bright_image(tmp_path: Path) -> Path:
    arr = np.full((100, 100, 3), 220)
    return _save(arr, tmp_path / "bright.jpg")


@pytest.fixture()
def symmetric_image(tmp_path: Path) -> Path:
    arr = np.zeros((100, 100, 3))
    arr[:, :50] = 128
    arr[:, 50:] = 128
    return _save(arr, tmp_path / "symmetric.jpg")


@pytest.fixture()
def two_color_image(tmp_path: Path) -> Path:
    arr = np.zeros((100, 100, 3))
    arr[:50, :] = [255, 0, 0]
    arr[50:, :] = [0, 0, 255]
    return _save(arr, tmp_path / "two_color.jpg")
