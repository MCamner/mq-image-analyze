"""Detect components, connections, and groups in architecture diagrams."""
from __future__ import annotations

import math
from pathlib import Path

import cv2  # type: ignore[import-untyped,import-not-found]
import numpy as np

from .observation import Component, Connection, Group


def _bgr_to_hex(b: float, g: float, r: float) -> str:
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def detect_components(image_path: str | Path, max_components: int = 30) -> list[Component]:
    """
    Detect rectangular box-like regions as architecture components.
    Uses Canny edge detection so fill color does not matter.
    Returns Component list sorted by top-left position (reading order).
    """
    bgr = cv2.imread(str(image_path))
    if bgr is None:
        return []

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    total_area = h * w

    # Fill-based detection: threshold non-white pixels (captures colored fills +
    # dark outlines), then morphologically open to remove thin connecting lines
    # (which are typically 1-3px wide) while preserving larger box fills.
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    # Opening kernel larger than expected line width — removes thin lines/arrows
    open_k = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_k)
    # Dilate slightly to restore approximate fill extent
    dilate_k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    filled = cv2.dilate(opened, dilate_k, iterations=1)

    contours, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < total_area * 0.002 or area > total_area * 0.7:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = max(bw, bh) / max(min(bw, bh), 1)
        if aspect >= 10:  # skip anything still line-shaped
            continue
        candidates.append((x, y, bw, bh, area))

    # Deduplicate heavily overlapping boxes (keep larger)
    candidates = _deduplicate(candidates)

    # Sort by reading order (top-to-bottom, left-to-right)
    candidates.sort(key=lambda c: (c[1] // 50, c[0]))

    components = []
    for idx, (x, y, bw, bh, area) in enumerate(candidates[:max_components]):
        fill = _dominant_fill(bgr, x, y, bw, bh)
        components.append(Component(
            id=f"box_{idx}",
            bbox=[float(x), float(y), float(x + bw), float(y + bh)],
            area_percent=round(area / total_area * 100, 2),
            fill_color=fill,
        ))

    return components


def detect_connections(image_path: str | Path, components: list[Component]) -> list[Connection]:
    """
    Detect lines/arrows between components by finding elongated contours
    that span between component bounding boxes.
    """
    bgr = cv2.imread(str(image_path))
    if bgr is None:
        return []

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    total_area = h * w

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    connections = []
    conn_idx = 0
    comp_boxes = [(c.id, c.bbox) for c in components]

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < total_area * 0.0003 or area > total_area * 0.05:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        aspect = max(bw, bh) / max(min(bw, bh), 1)
        if aspect < 4:  # must be elongated to be a line
            continue

        direction = _line_direction(bw, bh)
        from_id = _nearest_component(x, y, comp_boxes, side="start", direction=direction)
        to_id = _nearest_component(x + bw, y + bh, comp_boxes, side="end", direction=direction)

        if from_id == to_id:
            continue

        connections.append(Connection(
            id=f"edge_{conn_idx}",
            direction=direction,
            from_component=from_id,
            to_component=to_id,
        ))
        conn_idx += 1

    return connections[:20]  # cap at 20 connections


def detect_groups(components: list[Component]) -> list[Group]:
    """
    Group components by similar fill_color.
    Components with no fill_color or white/near-white fill are ungrouped.
    """
    color_map: dict[str, list[str]] = {}

    for comp in components:
        if comp.fill_color is None:
            continue
        r = int(comp.fill_color[1:3], 16)
        g = int(comp.fill_color[3:5], 16)
        b = int(comp.fill_color[5:7], 16)
        brightness = (r + g + b) / 3
        if brightness > 230:  # near-white — skip
            continue

        # Quantize to broad color bucket (64-level)
        bucket = f"#{(r >> 6) << 6:02x}{(g >> 6) << 6:02x}{(b >> 6) << 6:02x}"
        color_map.setdefault(bucket, []).append(comp.id)

    groups = []
    for color, ids in color_map.items():
        if len(ids) >= 2:
            groups.append(Group(color=color, component_ids=ids))

    return groups


def infer_dominant_flow(components: list[Component]) -> str:
    """Infer dominant layout flow from component positions."""
    if len(components) < 3:
        return "unknown"

    xs = [(c.bbox[0] + c.bbox[2]) / 2 for c in components]
    ys = [(c.bbox[1] + c.bbox[3]) / 2 for c in components]

    x_spread = max(xs) - min(xs)
    y_spread = max(ys) - min(ys)

    if x_spread < 50 and y_spread < 50:
        return "unknown"
    if x_spread > y_spread * 1.5:
        return "left-to-right"
    if y_spread > x_spread * 1.5:
        return "top-to-bottom"
    return "radial"


# ── helpers ───────────────────────────────────────────────────────────────────

def _dominant_fill(bgr: np.ndarray, x: int, y: int, bw: int, bh: int) -> str | None:
    """Sample the center region of a box and return dominant hex color."""
    pad = max(5, min(bw, bh) // 6)
    cx1, cy1 = x + pad, y + pad
    cx2, cy2 = x + bw - pad, y + bh - pad
    if cx2 <= cx1 or cy2 <= cy1:
        return None
    region = bgr[cy1:cy2, cx1:cx2]
    if region.size == 0:
        return None
    mean_color = cv2.mean(region)[:3]
    return _bgr_to_hex(*mean_color)


def _deduplicate(candidates: list[tuple]) -> list[tuple]:
    """Remove heavily overlapping boxes (IoU > 0.5), keeping the larger one."""
    result: list[tuple] = []
    for cand in sorted(candidates, key=lambda c: -c[4]):
        x1, y1, w1, h1, a1 = cand
        dominated = False
        for x2, y2, w2, h2, a2 in result:
            ix = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            iy = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
            inter = ix * iy
            union = a1 + a2 - inter
            if union > 0 and inter / union > 0.5:
                dominated = True
                break
        if not dominated:
            result.append(cand)
    return result


def _line_direction(bw: int, bh: int) -> str:
    if bw > bh * 2:
        return "horizontal"
    if bh > bw * 2:
        return "vertical"
    return "diagonal"


def _nearest_component(
    px: float,
    py: float,
    comp_boxes: list[tuple[str, list[float]]],
    side: str,
    direction: str,
) -> str | None:
    best_id = None
    best_dist = float("inf")
    for cid, bbox in comp_boxes:
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        dist = math.hypot(px - cx, py - cy)
        if dist < best_dist:
            best_dist = dist
            best_id = cid
    # Only claim a match if within reasonable distance
    return best_id if best_dist < 300 else None
