from __future__ import annotations

from pathlib import Path

from mq_image_analyze.vision.semantic.ollama_vision import describe as ollama_describe
from mq_image_analyze.vision.semantic.openai_vision import describe as openai_describe

VisionMode = str

DEFAULT_LOCAL_FAST_MODEL = "bakllava"
DEFAULT_LOCAL_DEEP_MODEL = "llama3.2-vision"
DEFAULT_CLOUD_VERIFY_MODEL = "gpt-4.1"

_VALID_VISION_MODES = {"local-fast", "local-deep", "cloud-verify"}


def normalize_vision_mode(vision_mode: str | None) -> str:
    mode = (vision_mode or "local-fast").strip().lower()
    if mode in {"ollama", "local", "fast"}:
        return "local-fast"
    if mode in {"deep", "ollama-deep"}:
        return "local-deep"
    if mode in {"gpt", "openai", "cloud", "verify", "gpt-4o", "gpt-4.1"}:
        return "cloud-verify"
    if mode not in _VALID_VISION_MODES:
        raise ValueError(
            f"Unsupported vision mode: {vision_mode}. "
            "Use local-fast, local-deep, or cloud-verify."
        )
    return mode


def default_model_for_mode(vision_mode: str) -> str:
    if vision_mode == "local-deep":
        return DEFAULT_LOCAL_DEEP_MODEL
    if vision_mode == "cloud-verify":
        return DEFAULT_CLOUD_VERIFY_MODEL
    return DEFAULT_LOCAL_FAST_MODEL


def describe(
    image_path: str | Path,
    vision_mode: str = "local-fast",
    vision_model: str | None = None,
    nudenet_context: dict | None = None,
) -> tuple[str | None, str, str]:
    mode = normalize_vision_mode(vision_mode)
    model = vision_model or default_model_for_mode(mode)

    if mode == "cloud-verify":
        caption = openai_describe(image_path, model=model, nudenet_context=nudenet_context)
    else:
        caption = ollama_describe(image_path, model=model, nudenet_context=nudenet_context)

    return caption, mode, model
