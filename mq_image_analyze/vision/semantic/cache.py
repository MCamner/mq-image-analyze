"""On-disk cache for semantic captions, used only when a caller asks for it.

The key covers everything that changes the answer: image bytes, vision mode,
model, whether the upload was redacted, and the prompt text. Location is
$MQ_IMAGE_CACHE_DIR, else ~/.cache/mq-image-analyze/captions.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def cache_dir() -> Path:
    raw = os.environ.get("MQ_IMAGE_CACHE_DIR")
    return Path(raw).expanduser() if raw else Path.home() / ".cache" / "mq-image-analyze" / "captions"


def key(image_path: Path, *, vision_mode: str, vision_model: str, redacted: bool, prompt: str) -> str:
    h = hashlib.sha256(Path(image_path).read_bytes())
    for part in (vision_mode, vision_model, "redacted" if redacted else "original", prompt):
        h.update(b"\0" + part.encode("utf-8"))
    return h.hexdigest()


def get(cache_key: str) -> str | None:
    try:
        data = json.loads((cache_dir() / f"{cache_key}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    caption = data.get("caption")
    return caption if isinstance(caption, str) and caption else None


def put(cache_key: str, caption: str) -> None:
    directory = cache_dir()
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{cache_key}.json").write_text(json.dumps({"caption": caption}), encoding="utf-8")
