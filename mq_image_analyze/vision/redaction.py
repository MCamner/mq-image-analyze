"""Mask personal identifiers before an image is sent to a cloud vision model.

Only used for cloud-verify, and only when asked for. It finds Swedish
personnummer/samordningsnummer and email addresses with OCR and paints their
boxes black on a copy. It cannot find what OCR cannot read — handwriting,
small or rotated text, faces — so it reduces exposure rather than removing it.

Fail-closed: if redaction was requested and OCR cannot run, the caller gets no
path back and must not send the image.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw

from mq_image_analyze.pipelines.ocr_pipeline import OcrUnavailable, Word
from mq_image_analyze.pipelines.ocr_pipeline import ocr_words as _ocr_words

_PERSONNUMMER = re.compile(r"^(?:19|20)?\d{6}[-+]?\d{4}$")
_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")
_STRIP = ".,;:()[]<>\"'"


@dataclass
class RedactionResult:
    path: Path | None
    redacted: int
    notes: list[str] = field(default_factory=list)


def _is_sensitive(text: str) -> bool:
    text = text.strip(_STRIP)
    return bool(_PERSONNUMMER.match(text) or _EMAIL.match(text))


def _sensitive_boxes(words: list[Word]) -> list[tuple[int, int, int, int]]:
    hits: set[int] = set()
    for i, (text, _, line) in enumerate(words):
        if _is_sensitive(text):
            hits.add(i)
        # "800101 1234" is often read as two words on the same line.
        if i + 1 < len(words) and words[i + 1][2] == line:
            if _PERSONNUMMER.match(text.strip(_STRIP) + words[i + 1][0].strip(_STRIP)):
                hits.update((i, i + 1))
    return [words[i][1] for i in sorted(hits)]


def redact_for_cloud(image_path: Path, out_dir: Path) -> RedactionResult:
    """Write a masked copy into out_dir, or return path=None when OCR cannot run."""
    with Image.open(image_path) as src:
        img = src.convert("RGB")
    try:
        words = _ocr_words(img)
    except OcrUnavailable as exc:
        return RedactionResult(
            path=None,
            redacted=0,
            notes=[f"Redaction requested but OCR unavailable ({exc}) — image not sent to cloud-verify."],
        )

    boxes = _sensitive_boxes(words)
    draw = ImageDraw.Draw(img)
    for box in boxes:
        draw.rectangle(box, fill=(0, 0, 0))
    out = out_dir / "redacted.png"
    img.save(out)
    return RedactionResult(
        path=out,
        redacted=len(boxes),
        notes=[
            f"Redaction: {len(boxes)} region(s) masked (personnummer, email) before cloud-verify. "
            "Only OCR-readable text is covered."
        ],
    )
