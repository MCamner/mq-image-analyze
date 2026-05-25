from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

try:
    from nudenet import NudeDetector as _NudeDetector  # type: ignore[import-untyped]
except ImportError:
    _NudeDetector = None

_NUDITY_CLASSES = {
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ARMPITS_EXPOSED",
    "BELLY_EXPOSED",
}

_FULL_NUDITY_CLASSES = {
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED",
}

_CONF_THRESHOLD = 0.5
_detector: Any = None


def _get_detector() -> Any:
    global _detector
    if _detector is None:
        assert _NudeDetector is not None
        _detector = _NudeDetector()
    return _detector


def classify(image_path: str | Path) -> dict:
    """Run NudeNet on image and return content_flags dict."""
    if _NudeDetector is None:
        return _not_implemented("nudenet not installed — run: pip install nudenet")

    detector = _get_detector()
    raw = detector.detect(str(image_path))
    hits = [d for d in raw if d.get("score", 0) >= _CONF_THRESHOLD]
    hit_classes = {d["class"] for d in hits}

    def best_conf(classes: set) -> float | None:
        scores = [d["score"] for d in hits if d["class"] in classes]
        return round(max(scores), 4) if scores else None

    nudity_hits      = hit_classes & (_NUDITY_CLASSES | _FULL_NUDITY_CLASSES)
    full_nudity_hits = hit_classes & _FULL_NUDITY_CLASSES

    return {
        "nudity": {
            "detected": bool(nudity_hits),
            "confidence": best_conf(_NUDITY_CLASSES | _FULL_NUDITY_CLASSES),
        },
        "full_nudity": {
            "detected": bool(full_nudity_hits),
            "confidence": best_conf(_FULL_NUDITY_CLASSES),
        },
        "sexual_activity": {
            "detected": False,
            "confidence": None,
        },
        "source": "nudenet",
        "raw_classes": sorted(hit_classes),
        "note": (
            "sexual_activity detection not available in NudeNet — "
            "requires additional classifier."
        ),
    }


def _not_implemented(note: str) -> dict:
    return {
        "nudity":          {"detected": False, "confidence": None},
        "full_nudity":     {"detected": False, "confidence": None},
        "sexual_activity": {"detected": False, "confidence": None},
        "source": "not_implemented",
        "note": note,
    }
