from __future__ import annotations

from mq_image_analyze.web.server import _WEB_DIR


def test_web_index_is_packaged_with_server() -> None:
    index = _WEB_DIR / "index.html"

    assert index.exists()
    assert "mq-image-analyze" in index.read_text()
