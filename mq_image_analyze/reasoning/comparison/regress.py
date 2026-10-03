"""Visual regression: a directory of baseline screenshots against current ones.

Screens are paired by file name. A screen is changed when pixels differ by
more than PIXEL_THRESHOLD in at least one region large enough to survive the
noise filter, and the share of changed pixels (`changed_ratio`) exceeds the
threshold. The threshold is on that share, not on the mean `pixel_diff`: a
renamed button moves the mean by about 0.001 and would pass any useful mean
threshold. A screen missing from current fails; one only in current is new.

Pixel comparison only: this says where a screen changed, not whether the
change was intended.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from mq_image_analyze.formats import IMAGE_EXTENSIONS
from mq_image_analyze.reasoning.comparison.comparator import _pixel_diff

#: Grayscale difference (0–255) below which a pixel counts as unchanged, so
#: anti-aliasing and compression noise do not light up the whole screen.
PIXEL_THRESHOLD = 25
#: Regions smaller than this share of the image are dropped as noise.
MIN_REGION_AREA = 0.0005
MAX_REGIONS = 50


@dataclass
class RegressEntry:
    name: str
    status: str  # unchanged | changed | missing | new
    baseline: str | None
    current: str | None
    pixel_diff: float | None = None
    changed_ratio: float | None = None
    size_changed: bool | None = None
    regions: list[dict] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return self.status in ("changed", "missing")


@dataclass
class RegressReport:
    fail_over: float
    entries: list[RegressEntry]

    @property
    def failed(self) -> int:
        return sum(e.failed for e in self.entries)


def _gray(path: Path, size: tuple[int, int] | None = None) -> np.ndarray:
    with Image.open(path) as img:
        gray = img.convert("L")
        if size is not None and gray.size != size:
            gray = gray.resize(size)
        return np.asarray(gray, dtype=np.uint8)


def _changes(before: Path, after: Path) -> tuple[float, list[dict]]:
    """(share of changed pixels, boxes around them in `before`'s coordinates)."""
    b = _gray(before)
    a = _gray(after, size=(b.shape[1], b.shape[0]))
    mask = (cv2.absdiff(b, a) > PIXEL_THRESHOLD).astype(np.uint8) * 255
    if not mask.any():
        return 0.0, []
    ratio = round(float(np.count_nonzero(mask)) / mask.size, 6)
    # Join nearby changed pixels into one region instead of one box per glyph.
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    total = b.shape[0] * b.shape[1]
    regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h < max(4, total * MIN_REGION_AREA):
            continue
        regions.append({
            "bbox": [x, y, x + w - 1, y + h - 1],
            "area_percent": round(100 * w * h / total, 2),
        })
    regions.sort(key=lambda r: r["area_percent"], reverse=True)
    return ratio, regions[:MAX_REGIONS]


def changed_regions(before: Path, after: Path) -> list[dict]:
    """Boxes around changed pixels, in `before`'s coordinates, largest first."""
    return _changes(before, after)[1]


def _images(directory: Path) -> dict[str, Path]:
    return {
        p.name: p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    }


def regress(baseline_dir: Path, current_dir: Path, *, fail_over: float) -> RegressReport:
    baseline = _images(Path(baseline_dir))
    current = _images(Path(current_dir))
    entries = []
    for name in sorted(baseline.keys() | current.keys()):
        b, c = baseline.get(name), current.get(name)
        if c is None:
            entries.append(RegressEntry(name, "missing", str(b), None))
            continue
        if b is None:
            entries.append(RegressEntry(name, "new", None, str(c)))
            continue
        diff, size_changed = _pixel_diff(b, c)
        ratio, regions = _changes(b, c)
        changed = size_changed or (bool(regions) and ratio > fail_over)
        entries.append(RegressEntry(
            name=name,
            status="changed" if changed else "unchanged",
            baseline=str(b),
            current=str(c),
            pixel_diff=diff,
            changed_ratio=ratio,
            size_changed=size_changed,
            regions=regions,
        ))
    return RegressReport(fail_over=fail_over, entries=entries)
