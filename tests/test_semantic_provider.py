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
    assert default_model_for_mode("local-fast") == "bakllava"
    assert default_model_for_mode("local-deep") == "llama3.2-vision"
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
