"""Visual regression: a directory of baseline screenshots against current ones.

Screens are paired by file name. A screen is changed when pixels differ by
more than PIXEL_THRESHOLD in at least one region large enough to survive the
noise filter, and the share of changed pixels (`changed_ratio`) exceeds the
threshold. The threshold is on that share, not on the mean `pixel_diff`: a
renamed button moves the mean by about 0.001 and would pass any useful mean
threshold. A screen missing from current fails; one only in current is new.

Ignored regions (clocks, dates, user names) are cleared from the change mask
before anything is counted, so changes there never fail a screen.

On changed screens the text inside each region is read with OCR (text_diff),
so a region is `changed`/`added`/`removed` text or `visual` only. With
fail_on="text" a screen fails only on a text change, a size change or when it
is missing; if OCR cannot run it fails anyway rather than pass unread.

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
from mq_image_analyze.pipelines.ocr_pipeline import OcrUnavailable
from mq_image_analyze.reasoning.comparison import text_diff
from mq_image_analyze.reasoning.comparison.comparator import _pixel_diff

#: Per-channel difference (0–255) below which a pixel counts as unchanged, so
#: anti-aliasing and compression noise do not light up the whole screen.
#: Per channel, not grayscale: blue to darker blue barely moves gray.
PIXEL_THRESHOLD = 25
#: Regions smaller than this share of the image are dropped as noise.
MIN_REGION_AREA = 0.0005
MAX_REGIONS = 50
FAIL_ON = ("any", "text")

Box = tuple[int, int, int, int]
#: (screen name or None for every screen, box in baseline pixels, inclusive)
Ignore = tuple[str | None, Box]


def parse_ignore(specs: list[str]) -> list[Ignore]:
    """`x1,y1,x2,y2` for every screen, or `name.png:x1,y1,x2,y2` for one."""
    parsed: list[Ignore] = []
    for spec in specs:
        name, _, coords = spec.rpartition(":")
        parts = coords.split(",")
        try:
            x1, y1, x2, y2 = (int(p) for p in parts)
        except ValueError as exc:
            raise ValueError(f"ignore region must be [name:]x1,y1,x2,y2 with integers, got {spec!r}") from exc
        if x2 < x1 or y2 < y1 or min(x1, y1) < 0:
            raise ValueError(f"ignore region needs 0 <= x1 <= x2 and 0 <= y1 <= y2, got {spec!r}")
        parsed.append((name or None, (x1, y1, x2, y2)))
    return parsed


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
    ignored_regions: list[list[int]] = field(default_factory=list)
    text_changes: list[dict] = field(default_factory=list)
    #: "available", "unavailable", or None when OCR was not attempted
    text_ocr: str | None = None
    #: Set by regress() from fail_on; None falls back to the status.
    fails: bool | None = None

    @property
    def failed(self) -> bool:
        if self.fails is not None:
            return self.fails
        return self.status in ("changed", "missing")


@dataclass
class RegressReport:
    fail_over: float
    entries: list[RegressEntry]

    @property
    def failed(self) -> int:
        return sum(e.failed for e in self.entries)


def _rgb(path: Path, size: tuple[int, int] | None = None) -> np.ndarray:
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        if size is not None and rgb.size != size:
            rgb = rgb.resize(size)
        return np.asarray(rgb, dtype=np.uint8)


def _changes(before: Path, after: Path, ignore: list[Box] = ()) -> tuple[float, list[dict]]:
    """(share of changed pixels, boxes around them in `before`'s coordinates)."""
    b = _rgb(before)
    a = _rgb(after, size=(b.shape[1], b.shape[0]))
    mask = (cv2.absdiff(b, a).max(axis=2) > PIXEL_THRESHOLD).astype(np.uint8) * 255
    for x1, y1, x2, y2 in ignore:
        mask[y1 : y2 + 1, x1 : x2 + 1] = 0
    if not mask.any():
        return 0.0, []
    ratio = round(float(np.count_nonzero(mask)) / mask.size, 6)
    # Join nearby changed pixels into one region instead of one box per glyph;
    # wider than tall so the words of one line become one region.
    mask = cv2.dilate(mask, np.ones((5, 15), np.uint8))
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


def _fails(entry: RegressEntry, fail_on: str) -> bool:
    if entry.status == "missing":
        return True
    if entry.status != "changed":
        return False
    if fail_on == "any" or entry.size_changed or entry.text_ocr != "available":
        return True
    return any(change["kind"] != "visual" for change in entry.text_changes)


def regress(
    baseline_dir: Path,
    current_dir: Path,
    *,
    fail_over: float,
    ignore: list[Ignore] = (),
    text: bool = True,
    fail_on: str = "any",
) -> RegressReport:
    if fail_on not in FAIL_ON:
        raise ValueError(f"fail_on must be one of {FAIL_ON}, got {fail_on!r}")
    baseline = _images(Path(baseline_dir))
    current = _images(Path(current_dir))
    entries = []
    for name in sorted(baseline.keys() | current.keys()):
        b, c = baseline.get(name), current.get(name)
        if c is None:
            entries.append(RegressEntry(name, "missing", str(b), None, fails=True))
            continue
        if b is None:
            entries.append(RegressEntry(name, "new", None, str(c), fails=False))
            continue
        diff, size_changed = _pixel_diff(b, c)
        boxes = [box for screen, box in ignore if screen in (None, name)]
        ratio, regions = _changes(b, c, boxes)
        changed = size_changed or (bool(regions) and ratio > fail_over)
        entry = RegressEntry(
            name=name,
            status="changed" if changed else "unchanged",
            baseline=str(b),
            current=str(c),
            pixel_diff=diff,
            changed_ratio=ratio,
            size_changed=size_changed,
            regions=regions,
            ignored_regions=[list(box) for box in boxes],
        )
        if changed and text and regions:
            try:
                entry.text_changes = text_diff.text_changes(b, c, regions)
                entry.text_ocr = "available"
            except OcrUnavailable:
                entry.text_ocr = "unavailable"
        entry.fails = _fails(entry, fail_on)
        entries.append(entry)
    return RegressReport(fail_over=fail_over, entries=entries)
