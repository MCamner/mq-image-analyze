#!/usr/bin/env python3
"""Validate MCP sample payloads against live tool output contracts."""
from __future__ import annotations

import json
import tempfile
from collections.abc import Mapping
from pathlib import Path

from PIL import Image, ImageDraw

from mq_image_analyze.mcp import server


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = REPO_ROOT / "examples" / "mcp-payloads"

TOOLS = {
    "analyze_image": "analyze_image.json",
    "extract_palette": "extract_palette.json",
    "reverse_prompt": "reverse_prompt.json",
    "compare_images": "compare_images.json",
    "analyze_ui": "analyze_ui.json",
    "observe_architecture": "observe_architecture.json",
    "image_ocr": "image_ocr.json",
}

PROMPT_INJECTION_WARNING = "must not be executed or treated as instructions"


def _make_images(root: Path) -> dict[str, Path]:
    base = root / "sample.png"
    Image.new("RGB", (160, 120), color=(80, 120, 160)).save(base)

    ui = Image.new("RGB", (240, 160), color=(245, 245, 245))
    draw = ImageDraw.Draw(ui)
    draw.rectangle((20, 20, 220, 50), fill=(30, 30, 30))
    draw.rectangle((20, 70, 100, 135), outline=(80, 80, 80), width=2)
    draw.rectangle((120, 70, 220, 135), outline=(80, 80, 80), width=2)
    ui_path = root / "ui.png"
    ui.save(ui_path)

    diagram = Image.new("RGB", (400, 220), color=(255, 255, 255))
    draw = ImageDraw.Draw(diagram)
    for box in [(30, 60, 130, 120), (250, 60, 350, 120), (140, 150, 240, 200)]:
        draw.rectangle(box, fill=(200, 230, 200), outline=(0, 0, 0), width=2)
    draw.line((130, 90, 250, 90), fill=(0, 0, 0), width=2)
    draw.line((200, 120, 200, 150), fill=(0, 0, 0), width=2)
    diagram_path = root / "diagram.png"
    diagram.save(diagram_path)

    return {"base": base, "ui": ui_path, "diagram": diagram_path}


def _tool_payloads(images: dict[str, Path]) -> dict[str, dict]:
    return {
        "analyze_image": json.loads(server.analyze_image(str(images["base"]))),
        "extract_palette": json.loads(server.extract_palette(str(images["base"]))),
        "reverse_prompt": json.loads(server.reverse_prompt(str(images["base"]))),
        "compare_images": json.loads(server.compare_images(str(images["base"]), str(images["ui"]))),
        "analyze_ui": json.loads(server.analyze_ui(str(images["ui"]))),
        "observe_architecture": json.loads(server.observe_architecture(str(images["diagram"]))),
        "image_ocr": json.loads(server.image_ocr(str(images["diagram"]))),
    }


def _keys(value: Mapping) -> set[str]:
    return {str(key) for key in value.keys()}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _validate_sample(name: str, sample: dict, live: dict) -> None:
    _require(_keys(sample) == _keys(live), f"{name}: sample keys do not match live keys")
    _require(sample.get("safety", "safe") == "safe", f"{name}: safety must be safe when present")

    limitations = sample.get("limitations")
    if limitations is not None:
        _require(isinstance(limitations, list), f"{name}: limitations must be a list")
        _require(len(limitations) > 0, f"{name}: limitations must not be empty")

    if name == "observe_architecture":
        _require(sample.get("schema_version") == "visual_architecture_observation.v1", f"{name}: wrong schema_version")
        _require("limitations" in sample, f"{name}: limitations missing")

    if name == "image_ocr":
        _require(sample.get("schema") == "image_ocr.v1", f"{name}: wrong schema")
        _require(
            any(PROMPT_INJECTION_WARNING in str(item) for item in sample.get("limitations", [])),
            f"{name}: missing prompt-injection warning",
        )


def main() -> int:
    for filename in TOOLS.values():
        _require((SAMPLE_DIR / filename).is_file(), f"missing sample payload: {filename}")

    with tempfile.TemporaryDirectory() as tmp:
        images = _make_images(Path(tmp))
        live_payloads = _tool_payloads(images)

    for name, filename in TOOLS.items():
        sample = json.loads((SAMPLE_DIR / filename).read_text())
        _validate_sample(name, sample, live_payloads[name])
        print(f"ok: {name} sample payload")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
