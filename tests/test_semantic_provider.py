from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from mq_image_analyze.vision.semantic.provider import (
    default_model_for_mode,
    describe,
    normalize_vision_mode,
)


def test_normalize_vision_mode_aliases() -> None:
    assert normalize_vision_mode("ollama") == "local-fast"
    assert normalize_vision_mode("openai") == "cloud-verify"
    assert normalize_vision_mode("gpt-4o") == "cloud-verify"


def test_default_models() -> None:
    assert default_model_for_mode("local-fast") == "qwen3.5:9b"
    assert default_model_for_mode("local-deep") == "qwen3.5:9b"
    assert default_model_for_mode("cloud-verify") == "gpt-4.1"


def test_cloud_verify_uses_openai_adapter(tmp_path: Path) -> None:
    image = tmp_path / "image.jpg"
    image.write_bytes(b"fake")

    with patch("mq_image_analyze.vision.semantic.provider.openai_describe", return_value="verified") as mock:
        caption, mode, model = describe(image, vision_mode="cloud-verify", vision_model="gpt-4o")

    assert caption == "verified"
    assert mode == "cloud-verify"
    assert model == "gpt-4o"
    mock.assert_called_once()


def test_failed_local_vision_does_not_call_cloud(tmp_path):
    image = tmp_path / "image.jpg"
    image.write_bytes(b"fake")
    with patch("mq_image_analyze.vision.semantic.provider.ollama_describe", return_value=None), patch("mq_image_analyze.vision.semantic.provider.openai_describe") as cloud:
        caption, mode, model = describe(image)
    assert caption is None
    assert mode == "local-fast"
    assert model == "qwen3.5:9b"
    cloud.assert_not_called()


def test_qwen_vision_request_disables_thinking_and_matches_exact_tag(tmp_path):
    import json
    from unittest.mock import MagicMock
    from mq_image_analyze.vision.semantic import ollama_vision
    image = tmp_path / "image.jpg"
    image.write_bytes(b"fake")
    response = MagicMock()
    response.__enter__.return_value.read.return_value = b'{"response":"caption","done":true}'
    with patch.object(ollama_vision.urllib.request, "urlopen", return_value=response) as opened:
        assert ollama_vision.describe(image) == "caption"
    payload = json.loads(opened.call_args.args[0].data)
    assert payload["model"] == "qwen3.5:9b"
    assert payload["think"] is False
    response.__enter__.return_value.read.return_value = b'{"models":[{"name":"qwen3.5:4b"}]}'
    with patch.object(ollama_vision.urllib.request, "urlopen", return_value=response):
        assert ollama_vision.is_available("qwen3.5:9b") is False


def test_caption_prompt_asks_for_image_type_and_photo_qualities():
    from mq_image_analyze.vision.semantic.ollama_vision import build_prompt

    for prompt in (build_prompt(None), build_prompt({"nudity": {"detected": True, "confidence": 0.9}})):
        lowered = prompt.lower()
        assert "first sentence" in lowered
        assert "photograph" in lowered
        assert "depth of field" in lowered
