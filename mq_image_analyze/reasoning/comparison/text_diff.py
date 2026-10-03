"""What text changed inside the regions where pixels changed.

Full-image OCR misses text on coloured backgrounds — white on a blue button
reads as nothing — so each region is read from its own crop, prepared for
OCR: grayscale, inverted when the background is dark, contrast stretched and
upscaled. The crop is first grown to the whole words full-image OCR found
overlapping the region, so a change to the last letter still reads the full
word. The result is what OCR read, not necessarily what the screen says.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, ImageStat

from mq_image_analyze.pipelines.ocr_pipeline import Word, ocr_words

_PAD = 4
_UPSCALE = 3


def classify(before: str, after: str) -> str:
    if before == after:
        return "visual"
    if not before:
        return "added"
    if not after:
        return "removed"
    return "changed"


def _overlaps(box, region) -> bool:
    x1, y1, x2, y2 = box
    rx1, ry1, rx2, ry2 = region
    return x1 <= rx2 and rx1 <= x2 and y1 <= ry2 and ry1 <= y2


def read_box(region, before: list[Word], after: list[Word], size: tuple[int, int]) -> list[int]:
    """The region grown to every whole word that overlaps it, padded, inside the image."""
    x1, y1, x2, y2 = region
    for _, box, _ in (*before, *after):
        if _overlaps(box, region):
            x1, y1 = min(x1, box[0]), min(y1, box[1])
            x2, y2 = max(x2, box[2]), max(y2, box[3])
    width, height = size
    return [max(0, x1 - _PAD), max(0, y1 - _PAD), min(width - 1, x2 + _PAD), min(height - 1, y2 + _PAD)]


def _read(img: Image.Image, box: list[int]) -> str:
    crop = img.crop((box[0], box[1], box[2] + 1, box[3] + 1)).convert("L")
    if ImageStat.Stat(crop).mean[0] < 128:  # dark background: make text dark on light
        crop = ImageOps.invert(crop)
    crop = ImageOps.autocontrast(crop)
    crop = crop.resize((crop.width * _UPSCALE, crop.height * _UPSCALE), Image.LANCZOS)
    words = sorted(ocr_words(crop), key=lambda w: (w[2], w[1][0]))
    return " ".join(" ".join(text for text, _, _ in words).split())


def text_changes(before: Path, after: Path, regions: list[dict]) -> list[dict]:
    """Per-region text change. Raises OcrUnavailable when OCR cannot run.

    `after` is resized to `before` first so everything shares the regions'
    coordinates.
    """
    with Image.open(before) as b_img, Image.open(after) as a_img:
        b = b_img.convert("RGB")
        a = a_img.convert("RGB")
        if a.size != b.size:
            a = a.resize(b.size)
    full_b, full_a = ocr_words(b), ocr_words(a)
    changes = []
    for region in regions:
        box = read_box(region["bbox"], full_b, full_a, b.size)
        old, new = _read(b, box), _read(a, box)
        changes.append({"bbox": list(region["bbox"]), "kind": classify(old, new), "before": old, "after": new})
    return changes
