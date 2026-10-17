from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from PIL import Image
from ultralytics import YOLO

_MODEL_PATH = Path(__file__).parents[3] / "models" / "yolov8n.pt"
_SOURCE_MODEL = "yolov8n"
_model: YOLO | None = None


class ModelNotFoundError(RuntimeError):
    pass


def _get_model() -> YOLO:
    global _model
    if _model is None:
        if not _MODEL_PATH.exists():
            raise ModelNotFoundError(
                f"YOLO model not found: {_MODEL_PATH}\n"
                "Run: mq-image doctor  — or download yolov8n.pt manually."
            )
        _model = YOLO(str(_MODEL_PATH))
    return _model


class Detection(NamedTuple):
    label: str
    confidence: float
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2
    area_percent: float = 0.0
    source_model: str = _SOURCE_MODEL


def detect(image_path: str | Path, conf: float = 0.25) -> list[Detection]:
    # Decode before inference: YOLO's path loader can silently drop unreadable
    # input and return no predictions, hiding the read failure as an IndexError.
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
    except (OSError, ValueError, ModuleNotFoundError) as exc:
        if isinstance(exc, ModuleNotFoundError) and exc.name not in {"pi_heif", "pi_heif._pi_heif"}:
            raise
        raise ValueError(f"Cannot decode image: {image_path}") from exc

    predictions = _get_model()(image, conf=conf, verbose=False)
    if not predictions:
        raise RuntimeError("Object detector returned no prediction for the decoded image")
    results = predictions[0]
    h, w = results.orig_shape
    image_area = float(h * w)
    detections = []
    for box in results.boxes:
        label = results.names[int(box.cls)]
        confidence = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        area_pct = round(((x2 - x1) * (y2 - y1)) / image_area * 100, 2)
        detections.append(Detection(label, round(confidence, 4), (x1, y1, x2, y2), area_pct, _SOURCE_MODEL))
    return sorted(detections, key=lambda d: d.confidence, reverse=True)


def detect_labels(image_path: str | Path, conf: float = 0.25) -> list[str]:
    """Summary mode — unique labels only, sorted by highest confidence."""
    seen: dict[str, float] = {}
    for d in detect(image_path, conf=conf):
        if d.label not in seen or d.confidence > seen[d.label]:
            seen[d.label] = d.confidence
    return list(seen.keys())


def detect_all(image_path: str | Path, conf: float = 0.05) -> list[Detection]:
    """Exhaustive mode — all detections, including duplicates and low-confidence."""
    return detect(image_path, conf=conf)
