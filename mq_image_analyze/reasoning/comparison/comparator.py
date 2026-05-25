from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult, build


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _color_distance(a: str, b: str) -> float:
    """Euclidean RGB distance normalized to 0–1."""
    ra, ga, ba = _hex_to_rgb(a)
    rb, gb, bb = _hex_to_rgb(b)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5 / (3 * 255 ** 2) ** 0.5


def _palette_drift(before: list[str], after: list[str]) -> float:
    """Average nearest-neighbor color distance between two palettes."""
    if not before or not after:
        return 1.0
    total = 0.0
    for color in before:
        total += min(_color_distance(color, c) for c in after)
    return round(total / len(before), 4)


def _ai_look_score(result: ReversePromptResult) -> float:
    """
    Heuristic score 0–1 for AI-generated image characteristics.
    High symmetry + strong ROT alignment + few/no YOLO objects = more AI-like.
    """
    score = 0.0
    score += result.symmetry * 0.4
    score += result.rule_of_thirds * 0.3
    if not result.objects:
        score += 0.2
    elif len(result.objects) <= 1:
        score += 0.1
    if result.contrast == "low contrast":
        score += 0.1
    return round(min(score, 1.0), 4)


@dataclass
class CompareResult:
    before: str
    after: str
    palette_drift: float
    style_drift: float
    objects_added: list[str]
    objects_removed: list[str]
    brightness_changed: bool
    contrast_changed: bool
    depth_changed: bool
    composition_diff: dict
    ai_look: dict
    before_result: dict = field(default_factory=dict)
    after_result: dict = field(default_factory=dict)


def compare(
    before_path: str | Path,
    after_path: str | Path,
    mode: str = "summary",
    conf: float | None = None,
) -> CompareResult:
    before_path = Path(before_path)
    after_path = Path(after_path)

    b = build(before_path, mode=mode, conf=conf)
    a = build(after_path, mode=mode, conf=conf)

    palette_drift = _palette_drift(b.palette, a.palette)

    brightness_changed = b.brightness != a.brightness
    contrast_changed = b.contrast != a.contrast
    depth_changed = b.depth != a.depth

    sym_delta = round(a.symmetry - b.symmetry, 4)
    rot_delta = round(a.rule_of_thirds - b.rule_of_thirds, 4)
    composition_diff = {
        "symmetry_delta": sym_delta,
        "rule_of_thirds_delta": rot_delta,
        "depth_changed": depth_changed,
        "composition_changed": b.composition != a.composition,
    }

    label_changes = round(
        (int(brightness_changed) + int(contrast_changed) + int(depth_changed)) / 3, 4
    )
    style_drift = round((palette_drift + abs(sym_delta) + label_changes) / 3, 4)

    before_set = set(b.objects)
    after_set = set(a.objects)

    ai_look = {
        "before": _ai_look_score(b),
        "after": _ai_look_score(a),
        "note": "Score 0–1: higher = more AI-generated characteristics (heuristic baseline).",
    }

    return CompareResult(
        before=str(before_path),
        after=str(after_path),
        palette_drift=palette_drift,
        style_drift=style_drift,
        objects_added=sorted(after_set - before_set),
        objects_removed=sorted(before_set - after_set),
        brightness_changed=brightness_changed,
        contrast_changed=contrast_changed,
        depth_changed=depth_changed,
        composition_diff=composition_diff,
        ai_look=ai_look,
        before_result={"prompt": b.prompt, "objects": b.objects, "palette": b.palette,
                       "brightness": b.brightness, "contrast": b.contrast, "depth": b.depth,
                       "symmetry": b.symmetry, "rule_of_thirds": b.rule_of_thirds},
        after_result={"prompt": a.prompt, "objects": a.objects, "palette": a.palette,
                      "brightness": a.brightness, "contrast": a.contrast, "depth": a.depth,
                      "symmetry": a.symmetry, "rule_of_thirds": a.rule_of_thirds},
    )
