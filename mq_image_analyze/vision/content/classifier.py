from __future__ import annotations

from pathlib import Path

# NudeNet class sets mapped to our three flags
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

_detector = None


def _get_detector():
    global _detector
    if _detector is None:
        from nudenet import NudeDetector
        _detector = NudeDetector()
    return _detector


def classify(image_path: str | Path) -> dict:
    """Run NudeNet on image and return content_flags dict."""
    try:
        detector = _get_detector()
    except ImportError:
        return _not_implemented("nudenet not installed — run: pip install nudenet")

    raw = detector.detect(str(image_path))
    hits = [d for d in raw if d.get("score", 0) >= _CONF_THRESHOLD]
    hit_classes = {d["class"] for d in hits}

    def best_conf(classes: set) -> float | None:
        scores = [d["score"] for d in hits if d["class"] in classes]
        return round(max(scores), 4) if scores else None

    nudity_hits     = hit_classes & (_NUDITY_CLASSES | _FULL_NUDITY_CLASSES)
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
