from __future__ import annotations

import io

from fastapi.testclient import TestClient
from PIL import Image

from mq_image_analyze.web.server import _WEB_DIR
from mq_image_analyze.web.server import app


def _image_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color=(0, 0, 0)).save(buf, format="JPEG")
    return buf.getvalue()


def test_web_index_is_packaged_with_server() -> None:
    index = _WEB_DIR / "index.html"

    assert index.exists()
    assert "mq-image-analyze" in index.read_text()


def test_web_analyze_rejects_invalid_conf() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/analyze",
        files={"file": ("test.jpg", _image_bytes(), "image/jpeg")},
        data={"conf": "abc"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "conf must be a number"


def test_web_analyze_rejects_invalid_vision_mode() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/analyze",
        files={"file": ("test.jpg", _image_bytes(), "image/jpeg")},
        data={"vision_mode": "not-real"},
    )

    assert response.status_code == 422
    assert "Unsupported vision mode" in response.json()["detail"]
