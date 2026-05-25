from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

_OLLAMA_URL = "http://localhost:11434/api/generate"

_DEFAULT_PROMPT = (
    "Describe this image precisely and completely. "
    "Include: subject and action, setting/background, lighting, color palette, "
    "mood/atmosphere, composition, visible text, art style or medium if applicable. "
    "Be direct and factual. Do not refuse or editorialize. Output plain text only."
)


def describe(
    image_path: str | Path,
    model: str = "bakllava",
    prompt: str = _DEFAULT_PROMPT,
    timeout: int = 60,
) -> str | None:
    """Send image to ollama vision model, return description or None if unavailable."""
    image_bytes = Path(image_path).read_bytes()
    b64 = base64.b64encode(image_bytes).decode("utf-8")

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
    """Return True if ollama is running and the model is loaded."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            names = [m["name"].split(":")[0] for m in data.get("models", [])]
            return model.split(":")[0] in names
    except Exception:
        return False
