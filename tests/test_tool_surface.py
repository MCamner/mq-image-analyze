"""mq-mcp.tool-surface.v1 for mq-image-analyze: the registered tools as a committed contract.

mq-agent calls image_perception and observe_architecture here. Its stack
compatibility gate checks those calls against a producer's committed
contracts/tool_surface.v1.json, and until this file existed both stayed
SKIPPED. The surface is generated from the in-process FastMCP registry, and
the class of every tool comes from TOOL_CLASSES, the same table /tools serves.
"""
import importlib.util
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from mq_image_analyze.mcp.http import app
from mq_image_analyze.mcp.server import TOOL_CLASSES

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts" / "tool_surface.v1.schema.json"
SURFACE = ROOT / "contracts" / "tool_surface.v1.json"

_spec = importlib.util.spec_from_file_location("export_tool_surface", ROOT / "scripts" / "export_tool_surface.py")
assert _spec and _spec.loader
export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export)


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_committed_surface_matches_the_registry() -> None:
    assert SURFACE.read_text(encoding="utf-8") == export.render(export.current_surface()), (
        "contracts/tool_surface.v1.json is stale — run: .venv/bin/python scripts/export_tool_surface.py"
    )


def test_committed_surface_is_valid(validator) -> None:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    assert list(validator.iter_errors(surface)) == []
    assert surface["producer"] == "mq-image-analyze"
    assert surface["tool_count"] == len(surface["tools"])


def test_tools_mq_agent_calls_are_published() -> None:
    names = {t["name"] for t in json.loads(SURFACE.read_text(encoding="utf-8"))["tools"]}
    assert {"image_perception", "observe_architecture"} <= names


def test_every_registered_tool_has_exactly_one_class() -> None:
    registered = {t["name"] for t in export.registered_tools()}
    assert set(TOOL_CLASSES) == registered
    assert set(TOOL_CLASSES.values()) <= {"A", "B", "C", "D"}


def test_a_tool_without_a_class_fails_the_export() -> None:
    with pytest.raises(ValueError, match="no ADR-003 class"):
        export.build_surface([{"name": "new_tool", "inputSchema": {}}], {})


def test_http_tools_serves_the_same_classes() -> None:
    tools = TestClient(app, base_url="http://localhost").get("/tools").json()["tools"]
    assert {t["name"]: t["class"] for t in tools} == TOOL_CLASSES


def test_parameters_and_signature_follow_the_input_schema() -> None:
    params = export.parameters_from_input_schema(
        {
            "properties": {"b": {"anyOf": [{"type": "string"}, {"type": "null"}]}, "a": {"type": "string"}},
            "required": ["a"],
        }
    )
    assert params == [
        {"name": "a", "type": ["string"], "required": True},
        {"name": "b", "type": ["null", "string"], "required": False},
    ]
    assert export.signature(params) == export.signature(json.loads(json.dumps(params)))
