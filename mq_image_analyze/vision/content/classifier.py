from __future__ import annotations

from pathlib import Path
from typing import Any

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
    "FEET_EXPOSED",
}

_FULL_NUDITY_CLASSES = {
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED",
}

_COVERED_CLASSES = {
    "FEMALE_BREAST_COVERED",
    "FEMALE_GENITALIA_COVERED",
    "BUTTOCKS_COVERED",
    "ANUS_COVERED",
    "BELLY_COVERED",
    "ARMPITS_COVERED",
    "FEET_COVERED",
}

_FACE_CLASSES = {
    "FACE_FEMALE",
    "FACE_MALE",
}

_CONF_THRESHOLD = 0.5
_detector: Any = None

_MODEL_640 = Path(__file__).parents[3] / "models" / "640m.onnx"


def _get_detector() -> Any:
    global _detector
    if _detector is None:
        assert _NudeDetector is not None
        if _MODEL_640.exists():
            _detector = _NudeDetector(model_path=str(_MODEL_640), inference_resolution=640)
        else:
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
    covered_hits     = hit_classes & _COVERED_CLASSES
    face_hits        = hit_classes & _FACE_CLASSES

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
        "faces": {
            "female": {
                "detected": "FACE_FEMALE" in face_hits,
                "confidence": best_conf({"FACE_FEMALE"}),
            },
            "male": {
                "detected": "FACE_MALE" in face_hits,
                "confidence": best_conf({"FACE_MALE"}),
            },
        },
        "covered_parts": sorted(covered_hits),
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
        "faces":           {"female": {"detected": False, "confidence": None},
                            "male":   {"detected": False, "confidence": None}},
        "covered_parts":   [],
        "source": "not_implemented",
        "note": note,
    }
