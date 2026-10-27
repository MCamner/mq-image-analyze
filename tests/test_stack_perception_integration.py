"""Opt-in integration with the real mq-agent bridge and mq-mcp validator.

Only HTTP transport is replaced with the image app's in-process transport.
No running services, language models or cloud credentials are needed.
"""
import importlib
import json
import os
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from mq_image_analyze.mcp.http import app
from mq_image_analyze.perception import from_architecture
from test_perception_contract import _release_gate_checks

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    os.environ.get("MQ_IMAGE_STACK_TESTS") != "1",
    reason="set MQ_IMAGE_STACK_TESTS=1 with mq-agent and mq-mcp checkouts",
)


@pytest.fixture
def consumers(monkeypatch):
    agent = Path(os.environ.get("MQ_AGENT_DIR", ROOT.parent / "mq-agent")).expanduser()
    checks = _release_gate_checks()
    assert (agent / "mq_agent").is_dir(), "MQ_AGENT_DIR must point to the mq-agent checkout"
    assert checks is not None, "MQ_MCP_DIR must point to the mq-mcp checkout or package"
    monkeypatch.syspath_prepend(str(agent))
    monkeypatch.syspath_prepend(str(checks.parent.parent))
    # Opt-in means missing consumer dependencies are failures, not silent skips.
    bridge = importlib.import_module("mq_agent.tools.mcp_bridge")
    contracts = importlib.import_module("mq_agent.tools.mcp_tool_contracts")
    gate = importlib.import_module("release_gate.checks")
    return bridge, contracts, gate


@pytest.fixture
def image_bridge(consumers, monkeypatch, tmp_path):
    bridge_module, _, _ = consumers
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path))
    with TestClient(app, base_url="http://localhost") as client:
        # Exercise real discovery, argument serialization and response parsing.
        monkeypatch.setattr(httpx, "get", lambda url, **kw: client.get(url))
        monkeypatch.setattr(httpx, "post", lambda url, **kw: client.post(url, json=kw["json"]))
        bridge = bridge_module.MCPBridge("http://localhost", source="mq-image-analyze")
        multi = bridge_module.MultiMCPBridge.__new__(bridge_module.MultiMCPBridge)
        multi.bridges = {"mq-image-analyze": bridge}
        yield bridge, multi


@pytest.fixture
def reference_image(tmp_path):
    path = tmp_path / "diagram.png"
    image = Image.new("RGB", (480, 240), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 60, 170, 160), fill="lightblue", outline="black", width=3)
    draw.rectangle((300, 60, 440, 160), fill="lightgreen", outline="black", width=3)
    draw.line((170, 110, 300, 110), fill="black", width=2)
    draw.text((60, 90), "Client", fill="black")
    draw.text((330, 90), "Server", fill="black")
    image.save(path)
    return path


def test_agent_accepts_published_image_tool_contract(consumers):
    _, contracts, _ = consumers
    relationships, findings = contracts.tool_contract_findings({"mq-image-analyze": ROOT})
    assert findings == []
    assert len(relationships) == 1
    assert relationships[0]["status"] == "PASS"


@pytest.mark.parametrize("producer", ["ui", "architecture", "ocr"])
def test_agent_perception_reaches_release_gate(
    consumers, image_bridge, reference_image, tmp_path, producer
):
    _, _, gate = consumers
    bridge, multi = image_bridge
    spec = bridge.describe_tool("image_perception")
    assert spec.safety_class == "read-only"
    assert {"image_path", "producer"} <= set(spec.input_schema["properties"])
    record = multi.image_perception(str(reference_image), producer=producer, source_type="diagram")
    assert isinstance(record, dict), record
    assert record["schema_version"] == "perception.v1"
    assert record["source_path"] == str(reference_image)
    assert record["limitations"]
    artifact = tmp_path / "perception.json"
    artifact.write_text(json.dumps(record), encoding="utf-8")
    assert gate._validate_perception_artifact(artifact) == []
    # Prove the real consumer rejects malformed evidence on the same path.
    del record["confidence"]
    artifact.write_text(json.dumps(record), encoding="utf-8")
    assert "missing confidence" in gate._validate_perception_artifact(artifact)


def test_agent_architecture_observation_normalizes_for_release_gate(
    consumers, image_bridge, reference_image, tmp_path
):
    _, _, gate = consumers
    bridge, multi = image_bridge
    assert bridge.describe_tool("observe_architecture").safety_class == "read-only"
    observation = multi.call_tool("observe_architecture", {"image_path": str(reference_image)})
    assert isinstance(observation, dict), observation
    assert observation["schema_version"] == "visual_architecture_observation.v1"
    assert observation["layout"]["component_count"] >= 2
    artifact = tmp_path / "architecture-perception.json"
    artifact.write_text(
        json.dumps(from_architecture(observation, source_type="diagram")), encoding="utf-8"
    )
    assert gate._validate_perception_artifact(artifact) == []


def test_agent_bridge_preserves_path_refusal(consumers, image_bridge, tmp_path):
    bridge, _ = image_bridge
    result = bridge.call_tool("observe_architecture", {"image_path": str(tmp_path.parent / "outside.png")})
    assert isinstance(result, str)
    assert "422" in result
    assert "outside MQ_IMAGE_ALLOWED_ROOTS" in result
