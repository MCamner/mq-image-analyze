from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


# ── helpers ──────────────────────────────────────────────────────────────────

def _load(image_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (bgr, gray) numpy arrays."""
    bgr = cv2.imread(str(image_path))
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return bgr, gray


def _avg_brightness(gray: np.ndarray) -> float:
    return float(np.mean(gray)) / 255.0


def _dominant_colors(bgr: np.ndarray, k: int = 3) -> list[tuple[int, int, int]]:
    """K-means dominant colors in RGB."""
    pixels = bgr.reshape(-1, 3).astype(np.float32)
    if len(pixels) > 5000:
        idx = np.random.choice(len(pixels), 5000, replace=False)
        pixels = pixels[idx]
    _, labels, centers = cv2.kmeans(
        pixels, k, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
        3, cv2.KMEANS_RANDOM_CENTERS,
    )
    counts = np.bincount(labels.flatten())
    order = np.argsort(-counts)
    result = []
    for i in order:
        b, g, r = centers[i]
        result.append((int(r), int(g), int(b)))
    return result


def _wcag_contrast(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """WCAG 2.1 contrast ratio between two RGB colors."""
    def relative_luma(c: tuple[int, int, int]) -> float:
        vals = [x / 255.0 for x in c]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in vals]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    l1 = relative_luma(c1)
    l2 = relative_luma(c2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def _text_density(gray: np.ndarray) -> str:
    """Estimate text density from horizontal edge count."""
    edges = cv2.Canny(gray, 50, 150)
    h, w = edges.shape
    row_activity = np.sum(edges > 0, axis=1) / w
    active_rows = float(np.mean(row_activity > 0.05))
    if active_rows > 0.55:
        return "high"
    if active_rows > 0.25:
        return "medium"
    return "low"


def _color_scheme(avg_brightness: float) -> str:
    if avg_brightness < 0.35:
        return "dark"
    if avg_brightness > 0.70:
        return "light"
    return "mixed"


def _detect_regions(bgr: np.ndarray) -> list[dict]:
    """Find large rectangular UI regions via edge contours."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 100)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = bgr.shape[:2]
    image_area = h * w
    regions = []
    for cnt in contours:
        x, y, rw, rh = cv2.boundingRect(cnt)
        area_pct = round(rw * rh / image_area * 100, 1)
        if area_pct < 2.0:
            continue
        rel_x = round(x / w, 3)
        rel_y = round(y / h, 3)
        rel_w = round(rw / w, 3)
        rel_h = round(rh / h, 3)
        role = _classify_region(rel_x, rel_y, rel_w, rel_h)
        regions.append({
            "role": role,
            "area_percent": area_pct,
            "position": {"x": rel_x, "y": rel_y, "w": rel_w, "h": rel_h},
        })
    regions.sort(key=lambda r: -r["area_percent"])
    return regions[:8]


def _classify_region(x: float, y: float, w: float, h: float) -> str:
    if y < 0.08 and h < 0.12:
        return "header/navbar"
    if y > 0.88 and h < 0.12:
        return "footer"
    if x < 0.15 and w < 0.25:
        return "sidebar-left"
    if x > 0.75 and w < 0.25:
        return "sidebar-right"
    if w > 0.6 and h > 0.5:
        return "main-content"
    return "panel"


def _hierarchy_depth(bgr: np.ndarray) -> int:
    """Estimate visual hierarchy depth from distinct brightness bands."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [16], [0, 256]).flatten()
    significant = np.sum(hist > (gray.size * 0.02))
    return int(min(max(significant // 2, 1), 5))


def _grid_alignment(bgr: np.ndarray) -> float:
    """Score 0–1: how well content aligns to a grid (via vertical edge consistency)."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    col_sums = np.sum(edges > 0, axis=0)
    h = edges.shape[0]
    strong_cols = np.sum(col_sums > h * 0.1)
    return round(min(strong_cols / max(edges.shape[1] * 0.1, 1), 1.0), 4)


# ── screenshot type detection ─────────────────────────────────────────────────

def _detect_screenshot_type(
    avg_brightness: float,
    color_scheme: str,
    text_density: str,
    dominant_colors: list[tuple[int, int, int]],
    bgr: np.ndarray,
) -> str:
    h, w = bgr.shape[:2]

    # Terminal: dark + high text density + near-monochrome palette
    if color_scheme == "dark" and text_density in ("high", "medium"):
        r, g, b = dominant_colors[0]
        saturation = max(r, g, b) - min(r, g, b)
        if saturation < 40:
            return "terminal"

    # Check for URL bar at very top (browser): thin strip with distinct color
    top_strip = bgr[:max(int(h * 0.06), 10), :]
    top_brightness = float(np.mean(cv2.cvtColor(top_strip, cv2.COLOR_BGR2GRAY))) / 255
    rest_brightness = float(np.mean(cv2.cvtColor(bgr[int(h * 0.06):, :], cv2.COLOR_BGR2GRAY))) / 255
    if abs(top_brightness - rest_brightness) > 0.25 and color_scheme == "light":
        return "browser"

    # README / docs: light background + medium-high text density + tall image
    if color_scheme == "light" and text_density in ("medium", "high") and h > w * 0.8:
        return "readme"

    # App UI: distinct regions, mixed or light
    if color_scheme in ("mixed", "light"):
        return "app-ui"

    return "unknown"


# ── contrast issues ───────────────────────────────────────────────────────────

def _accessibility_issues(
    contrast_ratio: float,
    text_density: str,
    color_scheme: str,
) -> list[str]:
    issues: list[str] = []
    if text_density in ("medium", "high") and contrast_ratio < 4.5:
        issues.append(f"Low text contrast ({contrast_ratio:.1f}:1 — WCAG AA requires 4.5:1 for normal text).")
    if text_density in ("medium", "high") and contrast_ratio < 3.0:
        issues.append("Very low contrast — likely fails WCAG AA for all text sizes.")
    if color_scheme == "dark" and contrast_ratio > 18:
        issues.append("Extremely high contrast — may cause halation on OLED displays.")
    return issues


# ── main ──────────────────────────────────────────────────────────────────────

_UI_LIMITATIONS = [
    "Layout regions detected via edge contours — semantic labels are heuristic.",
    "Text density estimated from edge activity, not OCR.",
    "Contrast ratio uses two dominant colors — may not reflect actual text/bg pair.",
    "AI-look score and hierarchy depth are heuristic baselines.",
    "No element-level detection (buttons, inputs, icons) without a specialized model.",
]


@dataclass
class UIAnalysisResult:
    screenshot_type: str
    color_scheme: str
    text_density: str
    contrast_ratio: float
    hierarchy_depth: int
    grid_alignment: float
    layout_regions: list[dict]
    issues: list[str]
    prompt: str
    semantic_caption: str | None = None
    limitations: list[str] = field(default_factory=lambda: list(_UI_LIMITATIONS))


def analyze_ui(image_path: str | Path) -> UIAnalysisResult:
    """Run UI/screenshot analysis on an image."""
    path = Path(image_path)
    bgr, gray = _load(path)

    avg_brightness = _avg_brightness(gray)
    dominant = _dominant_colors(bgr)
    scheme = _color_scheme(avg_brightness)
    density = _text_density(gray)
    regions = _detect_regions(bgr)
    hierarchy = _hierarchy_depth(bgr)
    grid = _grid_alignment(bgr)
    screenshot_type = _detect_screenshot_type(avg_brightness, scheme, density, dominant, bgr)

    # Contrast between two most dominant colors
    contrast = _wcag_contrast(dominant[0], dominant[1]) if len(dominant) >= 2 else 1.0
    issues = _accessibility_issues(contrast, density, scheme)

    # Try semantic caption via ollama
    try:
        from mq_image_analyze.vision.semantic.ollama_vision import describe
        ui_prompt = (
            f"This is a {screenshot_type} screenshot. "
            "Describe the UI layout, visible elements, content structure, "
            "color scheme, and any notable design patterns. Be factual and direct."
        )
        semantic_caption = describe(path, prompt=ui_prompt)
    except Exception:
        semantic_caption = None

    prompt_parts = [
        f"{screenshot_type} screenshot",
        f"{scheme} color scheme",
        f"{density} text density",
        f"contrast ratio {contrast:.1f}:1",
        f"hierarchy depth {hierarchy}",
        f"{len(regions)} layout regions",
    ]
    if issues:
        prompt_parts.append(f"{len(issues)} accessibility issue(s)")

    return UIAnalysisResult(
        screenshot_type=screenshot_type,
        color_scheme=scheme,
        text_density=density,
        contrast_ratio=contrast,
        hierarchy_depth=hierarchy,
        grid_alignment=grid,
        layout_regions=regions,
        issues=issues,
        prompt=", ".join(prompt_parts),
        semantic_caption=semantic_caption,
    )
