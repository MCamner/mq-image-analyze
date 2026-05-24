from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mq_image_analyze.vision.detection.detector import detect_labels
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


def build(image_path: str | Path) -> ReversePromptResult:
    path = Path(image_path)

    objects = detect_labels(path)
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

    palette_desc = ", ".join(palette[:3])
    obj_desc = ", ".join(objects[:5]) if objects else "no detected objects"

    prompt_parts = [
        obj_desc,
        f"{brightness} scene",
        contrast,
        depth,
        f"color palette: {palette_desc}",
        composition_desc,
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
        prompt=", ".join(p for p in prompt_parts if p),
    )
