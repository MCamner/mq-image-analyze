"""Classify image type for architecture observation."""
from __future__ import annotations

from pathlib import Path

import cv2  # type: ignore[import-untyped,import-not-found]
import numpy as np


def classify_image_type(image_path: str | Path) -> str:
    """
    Return one of: architecture-diagram | dashboard | terminal | ui-screenshot | unknown
    Uses purely structural/color heuristics — no model required.
    """
    bgr = cv2.imread(str(image_path))
    if bgr is None:
        return "unknown"

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    avg_brightness = float(np.mean(gray)) / 255.0
    is_dark = avg_brightness < 0.35

    # Count distinct rectangular regions (boxes)
    box_count = _count_boxes(gray)

    # Count horizontal edge rows (text density proxy)
    text_density = _text_density(gray)

    # Check if background is near-white or near-black
    corners = [
        bgr[0, 0], bgr[0, w - 1], bgr[h - 1, 0], bgr[h - 1, w - 1],
    ]
    corner_brightness = float(np.mean([np.mean(c) for c in corners])) / 255.0
    white_bg = corner_brightness > 0.85

    # Terminal: dark bg, high text density, monochrome
    if is_dark and text_density == "high":
        return "terminal"

    # Architecture diagram: white/light bg, multiple distinct boxes, moderate text
    if white_bg and box_count >= 4:
        return "architecture-diagram"

    # Dashboard: many grid-like regions, mixed colors
    if box_count >= 8:
        return "dashboard"

    # UI screenshot: tall image with light bg and structured regions
    aspect = h / w if w > 0 else 1.0
    if white_bg and aspect > 1.2 and box_count >= 2:
        return "ui-screenshot"

    if box_count >= 3:
        return "architecture-diagram"

    return "unknown"


def _count_boxes(gray: np.ndarray) -> int:
    """Count box-like regions using fill-based detection (morphological opening)."""
    h, w = gray.shape
    total_area = h * w
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    open_k = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_k)
    dilate_k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    filled = cv2.dilate(opened, dilate_k, iterations=1)
    contours, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < total_area * 0.002 or area > total_area * 0.7:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = max(bw, bh) / max(min(bw, bh), 1)
        if aspect < 8:
            count += 1
    return count


def _text_density(gray: np.ndarray) -> str:
    edges = cv2.Canny(gray, 50, 150)
    h, w = edges.shape
    row_hits = np.sum(edges > 0, axis=1)
    dense_rows = int(np.sum(row_hits > w * 0.05))
    ratio = dense_rows / max(h, 1)
    if ratio > 0.4:
        return "high"
    if ratio > 0.15:
        return "medium"
    return "low"
