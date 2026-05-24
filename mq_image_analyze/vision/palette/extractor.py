from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def extract(image_path: str | Path, n_colors: int = 6) -> list[str]:
    """Return top N dominant colors as hex strings, most dominant first."""
    img = cv2.imread(str(image_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    pixels = img.reshape(-1, 3).astype(np.float32)

    _, labels, centers = cv2.kmeans(
        pixels,
        n_colors,
        None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0),
        10,
        cv2.KMEANS_RANDOM_CENTERS,
    )

    counts = np.bincount(labels.flatten())
    order = np.argsort(counts)[::-1]

    return [
        "#{:02x}{:02x}{:02x}".format(int(centers[i][0]), int(centers[i][1]), int(centers[i][2]))
        for i in order
    ]


def brightness_label(image_path: str | Path) -> str:
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean = float(np.mean(gray))
    if mean < 60:
        return "dark"
    if mean < 130:
        return "mid-tone"
    return "bright"


def contrast_label(image_path: str | Path) -> str:
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    std = float(np.std(gray))
    if std < 30:
        return "low contrast"
    if std < 65:
        return "moderate contrast"
    return "high contrast"
