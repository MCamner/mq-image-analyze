from fastapi.testclient import TestClient
from PIL import Image
from mq_image_analyze.mcp.http import app


def test_http_discovery():
    client = TestClient(app, base_url="http://localhost")
    assert client.get('/health').json()['status'] == 'ok'
    tools = client.get('/tools').json()['tools']
    assert 'extract_palette' in {tool['name'] for tool in tools}
    assert all(tool['class'] == 'A' for tool in tools)


def test_http_tool_call_and_errors(tmp_path):
    client = TestClient(app, base_url="http://localhost")
    path = tmp_path / 'test.png'
    Image.new('RGB', (10, 10), 'red').save(path)
    response = client.post('/tools/extract_palette', json={'image_path': str(path)})
    assert response.status_code == 200
    assert response.json()['palette']
    assert client.post('/tools/no_such_tool', json={}).status_code == 404
    assert client.post('/tools/extract_palette', json={}).status_code == 422
    assert client.post('/tools/extract_palette', content='invalid').status_code == 422


def test_http_rejects_nonlocal_host():
    assert TestClient(app, base_url='http://evil.example').get('/tools').status_code == 400


def test_http_preserves_image_root_restrictions(tmp_path, monkeypatch):
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path / "allowed"))
    response = TestClient(app, base_url="http://localhost").post(
        "/tools/extract_palette", json={"image_path": str(tmp_path / "outside.png")}
    )
    assert response.status_code == 422
    assert "outside MQ_IMAGE_ALLOWED_ROOTS" in response.json()["detail"]


def test_cli_http_transport_uses_loopback_and_selected_port(monkeypatch):
    from typer.testing import CliRunner
    from mq_image_analyze.cli import app as cli
    calls = []
    monkeypatch.setattr('uvicorn.run', lambda *args, **kwargs: calls.append((args, kwargs)))
    response = CliRunner().invoke(cli, ['mcp', '--transport', 'http', '--port', '9876'])
    assert response.exit_code == 0, response.output
    assert calls == [(('mq_image_analyze.mcp.http:app',), {'host': '127.0.0.1', 'port': 9876})]


def test_http_rejects_browser_cross_origin_requests():
    """A web page can reach a loopback port. The bridge refuses any request
    that carries a non-loopback Origin, so a tool never runs on its behalf."""
    client = TestClient(app, base_url="http://127.0.0.1:8766")
    for origin in ("https://evil.example", "null"):
        response = client.post("/tools/extract_palette", json={"image_path": "/x.png"}, headers={"Origin": origin})
        assert response.status_code == 403, origin
        assert "Image not found" not in response.text
    for origin in ("http://localhost:3000", "http://127.0.0.1:8766", "http://[::1]:8766"):
        assert client.get("/health", headers={"Origin": origin}).status_code == 200, origin
    assert client.get("/health").status_code == 200  # mq-agent sends no Origin
