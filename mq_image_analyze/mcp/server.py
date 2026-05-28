from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mq-image-analyze")

# ── safety classification ──────────────────────────────────────────────────────
# All tools are read-only: they read image files and return analysis.
# No tool writes, deletes, or sends data externally.
# safety: "safe" = read-only, deterministic, no side-effects
_SAFETY = "safe"

_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}


def _validate_image(path: str) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")
    if p.suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported image format: {p.suffix} (allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))})")
    return p


# ── tools ─────────────────────────────────────────────────────────────────────

@mcp.tool(
    description=(
        "Analyze an image and return a full visual reasoning report: detected objects, "
        "color palette, brightness, contrast, depth, composition metrics, reverse prompt, "
        "content flags (nudity/explicit via NudeNet), and optional semantic caption "
        "(Ollama local-fast/local-deep or OpenAI cloud-verify). "
        f"Safety: {_SAFETY}. Read-only."
    )
)
def analyze_image(
    image_path: str,
    mode: str = "summary",
    conf: float | None = None,
    vision_mode: str = "local-fast",
    vision_model: str | None = None,
) -> str:
    """
    Args:
        image_path: Absolute or home-relative path to the image file.
        mode: 'summary' (default) or 'exhaustive' (all detections, low conf).
        conf: Detection confidence threshold. Defaults: 0.25 (summary), 0.05 (exhaustive).
        vision_mode: 'local-fast', 'local-deep', or 'cloud-verify'.
        vision_model: Optional backend model override, for example 'gpt-4o' or 'gpt-4.1'.
    Returns:
        JSON string with full ReversePromptResult.
    """
    from mq_image_analyze.reasoning.prompts.reverse_prompt import build
    p = _validate_image(image_path)
    result = build(p, mode=mode, conf=conf, vision_mode=vision_mode, vision_model=vision_model)
    return json.dumps(dataclasses.asdict(result), indent=2)


@mcp.tool(
    description=(
        "Extract the dominant color palette from an image. Returns up to 5 hex color codes "
        "with brightness and contrast labels. "
        f"Safety: {_SAFETY}. Read-only."
    )
)
def extract_palette(image_path: str) -> str:
    """
    Args:
        image_path: Absolute or home-relative path to the image file.
    Returns:
        JSON with palette (hex colors), brightness, and contrast.
    """
    from mq_image_analyze.vision.palette.extractor import (
        brightness_label,
        contrast_label,
        extract,
    )
    p = _validate_image(image_path)
    return json.dumps({
        "palette": extract(p),
        "brightness": brightness_label(p),
        "contrast": contrast_label(p),
        "safety": _SAFETY,
    }, indent=2)


@mcp.tool(
    description=(
        "Build a reverse prompt for an image — a structured text description suitable for "
        "AI image generators or visual search. Combines object detection, palette, composition, "
        "and optional semantic caption from local Ollama or cloud GPT vision. "
        f"Safety: {_SAFETY}. Read-only."
    )
)
def reverse_prompt(
    image_path: str,
    mode: str = "summary",
    vision_mode: str = "local-fast",
    vision_model: str | None = None,
) -> str:
    """
    Args:
        image_path: Absolute or home-relative path to the image file.
        mode: 'summary' or 'exhaustive'.
        vision_mode: 'local-fast', 'local-deep', or 'cloud-verify'.
        vision_model: Optional backend model override.
    Returns:
        JSON with prompt string, objects, palette, semantic_caption, and limitations.
    """
    from mq_image_analyze.reasoning.prompts.reverse_prompt import build
    p = _validate_image(image_path)
    result = build(p, mode=mode, vision_mode=vision_mode, vision_model=vision_model)
    d = dataclasses.asdict(result)
    return json.dumps({
        "prompt": d["prompt"],
        "semantic_caption": d["semantic_caption"],
        "objects": d["objects"],
        "palette": d["palette"],
        "limitations": d["limitations"],
        "safety": _SAFETY,
    }, indent=2)


@mcp.tool(
    description=(
        "Compare two images and return palette drift, style drift, composition differences, "
        "objects added/removed, and an AI-look heuristic score for each image. "
        f"Safety: {_SAFETY}. Read-only."
    )
)
def compare_images(
    before_path: str,
    after_path: str,
    mode: str = "summary",
) -> str:
    """
    Args:
        before_path: Path to the 'before' image.
        after_path: Path to the 'after' image.
        mode: 'summary' or 'exhaustive'.
    Returns:
        JSON with CompareResult including drift scores and composition diff.
    """
    from mq_image_analyze.reasoning.comparison.comparator import compare
    b = _validate_image(before_path)
    a = _validate_image(after_path)
    result = compare(b, a, mode=mode)
    return json.dumps(dataclasses.asdict(result), indent=2)


@mcp.tool(
    description=(
        "Analyze a UI screenshot: detects screenshot type (terminal/browser/readme/app-ui), "
        "layout regions, WCAG contrast ratio, text density, visual hierarchy depth, grid alignment, "
        "and accessibility issues. Optionally adds bakllava semantic caption. "
        f"Safety: {_SAFETY}. Read-only."
    )
)
def analyze_ui(image_path: str) -> str:
    """
    Args:
        image_path: Absolute or home-relative path to the screenshot.
    Returns:
        JSON with UIAnalysisResult including issues and WCAG contrast ratio.
    """
    from mq_image_analyze.vision.ui.analyzer import analyze_ui as _analyze_ui
    p = _validate_image(image_path)
    result = _analyze_ui(p)
    return json.dumps(dataclasses.asdict(result), indent=2)


@mcp.tool(
    description=(
        "Observe an architecture diagram or dashboard screenshot and return a structured "
        "visual_architecture_observation.v1 JSON blob designed for consumption by mq-mcp "
        "review tools. Detects rectangular components (boxes), connection lines/arrows, "
        "color-based groups, and image type (architecture-diagram | dashboard | terminal | "
        "ui-screenshot | unknown). OCR-based text extraction from boxes is included when "
        "pytesseract is installed. Output is optimized for injection into LLM review context. "
        f"Safety: {_SAFETY}. Read-only."
    )
)
def observe_architecture(image_path: str) -> str:
    """
    Args:
        image_path: Absolute or home-relative path to the diagram or screenshot.
    Returns:
        JSON string with visual_architecture_observation.v1 schema.
    """
    from mq_image_analyze.pipelines.architecture_pipeline import observe_architecture as _observe
    p = _validate_image(image_path)
    result = _observe(p)
    return json.dumps(dataclasses.asdict(result), indent=2)
