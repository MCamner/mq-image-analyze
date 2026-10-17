"""Regression tests for Qwen Vision through the HTTP tool bridge."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from mq_image_analyze.mcp.http import app


def test_http_analyze_image_uses_qwen_without_cloud_fallback(tmp_path):
    image = tmp_path / "red.png"
    Image.new("RGB", (64, 64), "red").save(image)

    client = TestClient(app, base_url="http://127.0.0.1:8766")

    with (
        patch(
            "mq_image_analyze.vision.semantic.provider.ollama_describe",
            return_value="A solid red image.",
        ) as local,
        patch(
            "mq_image_analyze.vision.semantic.provider.openai_describe"
        ) as cloud,
    ):
        response = client.post(
            "/tools/analyze_image",
            json={
                "image_path": str(image),
                "vision_mode": "local-fast",
            },
        )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["semantic_caption"] == "A solid red image."
    assert result["vision_mode"] == "local-fast"
    assert result["vision_model"] == "qwen3.5:9b"

    local.assert_called_once()
    cloud.assert_not_called()


def test_http_local_failure_never_calls_openai(tmp_path):
    image = tmp_path / "red.png"
    Image.new("RGB", (64, 64), "red").save(image)

    client = TestClient(app, base_url="http://127.0.0.1:8766")

    with (
        patch(
            "mq_image_analyze.vision.semantic.provider.ollama_describe",
            return_value=None,
        ),
        patch(
            "mq_image_analyze.vision.semantic.provider.openai_describe"
        ) as cloud,
    ):
        response = client.post(
            "/tools/analyze_image",
            json={
                "image_path": str(image),
                "vision_mode": "local-fast",
            },
        )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["vision_model"] == "qwen3.5:9b"
    assert result["semantic_caption"] is None

    cloud.assert_not_called()
