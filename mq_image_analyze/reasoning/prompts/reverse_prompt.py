from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mq_image_analyze.vision.content.classifier import classify as classify_content
from mq_image_analyze.vision.detection.detector import ModelNotFoundError, detect_all, detect_labels
from mq_image_analyze.vision.palette.extractor import (
    brightness_label,
    contrast_label,
    extract,
)
from mq_image_analyze.vision.composition.analyzer import (
    depth_label,
    rule_of_thirds_score,
    symmetry_score,
    visual_weight,
)
from mq_image_analyze.vision.semantic.ollama_vision import describe as ollama_describe

_SUMMARY_LIMITATIONS = [
    "Object detection limited to YOLOv8n COCO classes (80 categories).",
    "Low-confidence detections excluded (default conf < 0.25).",
    "Duplicate objects collapsed — count and position not preserved.",
    "OCR not active — visible text not analyzed.",
    "Semantic meaning and emotional context not inferred.",
    "content_flags require a specialized model — not active with YOLOv8n.",
]

_EXHAUSTIVE_LIMITATIONS = [
    "Object detection limited to YOLOv8n COCO classes (80 categories).",
    "Low-confidence detections included (conf >= 0.05) — verify before acting.",
    "Unclassified regions not yet implemented — non-COCO content not reported.",
    "OCR not active — visible text not analyzed.",
    "Semantic meaning and emotional context not inferred.",
    "content_flags require a specialized model — not active with YOLOv8n.",
]

_DEFAULT_CONTENT_FLAGS: dict = {
    "nudity": {"detected": False, "confidence": None},
    "full_nudity": {"detected": False, "confidence": None},
    "sexual_activity": {"detected": False, "confidence": None},
    "faces": {
        "female": {"detected": False, "confidence": None},
        "male":   {"detected": False, "confidence": None},
    },
    "covered_parts": [],
    "source": "not_implemented",
    "note": (
        "YOLOv8n does not classify explicit content. "
        "Attach a specialized content-classification model to populate these fields. "
        "This tool applies no suppression — all detector output is reported as-is."
    ),
}


@dataclass
class ReversePromptResult:
    objects: list[str]
    palette: list[str]
    brightness: str
    contrast: str
    depth: str
    composition: str
    symmetry: float
    rule_of_thirds: float
    prompt: str
    mode: str = "summary"
    detections: list[dict] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    text_regions: list[dict] = field(default_factory=list)
    unclassified_regions: list[dict] = field(default_factory=list)
    content_flags: dict = field(default_factory=lambda: dict(_DEFAULT_CONTENT_FLAGS))
    semantic_caption: str | None = None


def build(
    image_path: str | Path,
    mode: str = "summary",
    conf: float | None = None,
) -> ReversePromptResult:
    path = Path(image_path)

    effective_conf = conf if conf is not None else (0.05 if mode == "exhaustive" else 0.25)

    try:
        if mode == "exhaustive":
            raw = detect_all(path, conf=effective_conf)
            objects = list(dict.fromkeys(d.label for d in raw))
            detections = [
                {
                    "label": d.label,
                    "confidence": d.confidence,
                    "bbox": list(d.bbox),
                    "area_percent": d.area_percent,
                    "source_model": d.source_model,
                }
                for d in raw
            ]
            limitations = list(_EXHAUSTIVE_LIMITATIONS)
        else:
            objects = detect_labels(path, conf=effective_conf)
            detections = []
            limitations = list(_SUMMARY_LIMITATIONS)
    except ModelNotFoundError as exc:
        objects = []
        detections = []
        limitations = [f"Object detection unavailable: {exc}"]

    palette = extract(path)
    brightness = brightness_label(path)
    contrast = contrast_label(path)
    depth = depth_label(path)
    weight = visual_weight(path)
    rot = rule_of_thirds_score(path)
    sym = symmetry_score(path)

    composition_desc = weight
    if rot > 0.4:
        composition_desc += ", rule-of-thirds alignment"
    if sym > 0.85:
        composition_desc += ", strong symmetry"

    content_flags = classify_content(path)
    semantic_caption = ollama_describe(path, nudenet_context=content_flags)

    palette_desc = ", ".join(palette[:3])
    obj_desc = ", ".join(objects[:5]) if objects else "no detected objects"

    content_parts: list[str] = []
    for flag in ("nudity", "full_nudity", "sexual_activity"):
        entry = content_flags.get(flag, {})
        if entry.get("detected"):
            conf = entry.get("confidence")
            label = flag.replace("_", " ")
            content_parts.append(
                f"{label} ({round(conf * 100)}%)" if conf is not None else label
            )
    content_desc = "explicit content: " + ", ".join(content_parts) if content_parts else ""

    prompt_parts = [
        obj_desc,
        f"{brightness} scene",
        contrast,
        depth,
        f"color palette: {palette_desc}",
        composition_desc,
        content_desc,
    ]

    return ReversePromptResult(
        objects=objects,
        palette=palette,
        brightness=brightness,
        contrast=contrast,
        depth=depth,
        composition=composition_desc,
        symmetry=sym,
        rule_of_thirds=rot,
        prompt=semantic_caption or ", ".join(p for p in prompt_parts if p),
        mode=mode,
        detections=detections,
        limitations=limitations,
        text_regions=[],
        unclassified_regions=[],
        content_flags=content_flags,
        semantic_caption=semantic_caption,
    )
