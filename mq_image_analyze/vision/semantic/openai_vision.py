from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path

from mq_image_analyze.vision.semantic.ollama_vision import build_prompt

_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


def _image_data_url(image_path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(image_path))
    image_bytes = image_path.read_bytes()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime or 'image/jpeg'};base64,{b64}"


def _extract_response_text(data: dict) -> str | None:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
    return "\n".join(parts) or None


def describe(
    image_path: str | Path,
    model: str = "gpt-4.1",
    nudenet_context: dict | None = None,
    timeout: int = 90,
) -> str | None:
    """Send image to OpenAI vision-capable model and return a factual caption."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    path = Path(image_path)
    payload = json.dumps({
        "model": model,
        "input": [{
            "role": "user",
            "content": [
                {"type": "input_text", "text": build_prompt(nudenet_context)},
                {"type": "input_image", "image_url": _image_data_url(path)},
            ],
        }],
        "max_output_tokens": 700,
    }).encode("utf-8")

    req = urllib.request.Request(
        _OPENAI_RESPONSES_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return _extract_response_text(json.loads(resp.read()))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
