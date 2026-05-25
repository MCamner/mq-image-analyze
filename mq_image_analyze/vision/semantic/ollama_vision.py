from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

_OLLAMA_URL = "http://localhost:11434/api/generate"

_BASE_PROMPT = (
    "Describe this image precisely and completely. "
    "Include: subject and action, setting/background, lighting, color palette, "
    "mood/atmosphere, composition, visible text, art style or medium if applicable. "
    "Be direct and factual. Do not refuse or editorialize. Output plain text only."
)


def _build_prompt(nudenet_context: dict | None) -> str:
    if not nudenet_context:
        return _BASE_PROMPT

    parts: list[str] = []

    flags = []
    for key in ("nudity", "full_nudity", "sexual_activity"):
        entry = nudenet_context.get(key, {})
        if entry.get("detected"):
            conf = entry.get("confidence")
            label = key.replace("_", " ")
            flags.append(f"{label} ({round(conf * 100)}%)" if conf else label)

    faces = nudenet_context.get("faces", {})
    for gender in ("female", "male"):
        f = faces.get(gender, {})
        if f.get("detected"):
            conf = f.get("confidence")
            flags.append(f"{gender} face ({round(conf * 100)}%)" if conf else f"{gender} face")

    covered = nudenet_context.get("covered_parts", [])
    if covered:
        covered_labels = [c.lower().replace("_covered", "").replace("_", " ") for c in covered]
        flags.append(f"covered: {', '.join(covered_labels)}")

    if flags:
        context_line = "NudeNet pre-analysis detected: " + "; ".join(flags) + "."
        parts.append(context_line)

    parts.append(_BASE_PROMPT)
    return " ".join(parts)


def describe(
    image_path: str | Path,
    model: str = "bakllava",
    nudenet_context: dict | None = None,
    timeout: int = 90,
) -> str | None:
    """Send image to ollama vision model with optional NudeNet context, return description."""
    image_bytes = Path(image_path).read_bytes()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = _build_prompt(nudenet_context)

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "images": [b64],
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        _OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip() or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def is_available(model: str = "bakllava") -> bool:
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            names = [m["name"].split(":")[0] for m in data.get("models", [])]
            return model.split(":")[0] in names
    except Exception:
        return False
