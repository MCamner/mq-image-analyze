from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def rule_of_thirds_score(image_path: str | Path) -> float:
    """0–1 score for how well subjects align with rule-of-thirds grid lines."""
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    edges = cv2.Canny(gray, 50, 150)
    ys, xs = np.where(edges > 0)

    if len(xs) == 0:
        return 0.0

    thirds_x = [w / 3, 2 * w / 3]
    thirds_y = [h / 3, 2 * h / 3]
    tolerance = min(w, h) * 0.08

    near_x = sum(any(abs(x - t) < tolerance for t in thirds_x) for x in xs)
    near_y = sum(any(abs(y - t) < tolerance for t in thirds_y) for y in ys)
    total = len(xs) + len(ys)

    return round((near_x + near_y) / total, 3)


def symmetry_score(image_path: str | Path) -> float:
    """0–1 horizontal symmetry score."""
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(float)
    flipped = np.fliplr(gray)
    diff = np.abs(gray - flipped).mean()
    return round(1.0 - diff / 255.0, 3)


def visual_weight(image_path: str | Path) -> str:
    """Returns 'left-heavy', 'right-heavy', 'centered', or 'balanced'."""
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(float)
    h, w = gray.shape

    left = gray[:, : w // 2].mean()
    right = gray[:, w // 2 :].mean()
    top = gray[: h // 2, :].mean()
    bottom = gray[h // 2 :, :].mean()

    diff = abs(left - right)
    if diff < 5:
        return "balanced"
    return "left-heavy" if left > right else "right-heavy"


def depth_label(image_path: str | Path) -> str:
    """Coarse depth estimate from blur variance distribution."""
    img = cv2.imread(str(image_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    var = laplacian.var()
    if var < 100:
        return "shallow depth of field"
    if var < 500:
        return "moderate depth"
    return "deep / sharp throughout"
