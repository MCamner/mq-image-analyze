"""The normalized perception record, checked against the consumer that gates it.

mq-mcp's Release Gate v2 already validates perception artifacts and blocks a
release on an invalid one (`release_gate/checks.py`). The contract this repo
has to meet was therefore frozen there, not here: source_type from a fixed
enum, source_path, ocr_text, visual_summary, risk_signals as a list, confidence
from low/medium/high, and detected_regions as a list when present.

So the strongest test available is not a restatement of those rules — it is the
consumer's own validator, imported from the sibling checkout and run against
what this repo produces. When mq-mcp is not on the machine the structural
checks still run, and the cross-repo agreement is reported as unverified rather
than assumed.

The word `confidence` is the trap here. Every pipeline already produces a
per-region float: how sure the detector is about one box. The consumer wants
something else entirely — how complete the record is — and the two must not be
allowed to collapse into each other.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from mq_image_analyze import perception

ROOT = Path(__file__).resolve().parents[1]
PAYLOADS = ROOT / "examples" / "mcp-payloads"
FIXTURE = ROOT / "tests" / "fixtures" / "sample_perception_output.json"

def _release_gate_checks() -> Path | None:
    """mq-mcp's validator, wherever this machine keeps it.

    `MQ_MCP_DIR` names the *package* directory in existing callers, so the
    checkout is its parent — the same ambiguity mq-agent's `mq_mcp_root()`
    documents, resolved the same way rather than differently.
    """
    raw = os.environ.get("MQ_MCP_DIR", "")
    roots = (
        [Path(raw).expanduser(), Path(raw).expanduser().parent]
        if raw else [Path.home() / "mq-mcp"]
    )
    for root in roots:
        for candidate in (root / "release_gate" / "checks.py", root / "mq-mcp" / "release_gate" / "checks.py"):
            if candidate.is_file():
                return candidate
    return None


def payload(name: str) -> dict:
    return json.loads((PAYLOADS / name).read_text(encoding="utf-8"))


def consumer_errors(record: dict, tmp_path: Path) -> list[str]:
    """Run mq-mcp's own validator, or skip when this machine has no mq-mcp."""
    import sys

    checks = _release_gate_checks()
    if checks is None:
        pytest.skip("no mq-mcp checkout on this machine to validate against")
    package = str(checks.parent.parent)
    if package not in sys.path:
        sys.path.insert(0, package)
    from release_gate.checks import _validate_perception_artifact

    artifact = tmp_path / "perception.json"
    artifact.write_text(json.dumps(record), encoding="utf-8")
    return _validate_perception_artifact(artifact)


# ── the consumer decides ─────────────────────────────────────────────────────

def test_the_shipped_fixture_satisfies_the_consumer(tmp_path):
    """The artifact the gate will actually pick up."""
    assert consumer_errors(json.loads(FIXTURE.read_text(encoding="utf-8")), tmp_path) == []


def test_an_ocr_record_satisfies_the_consumer(tmp_path):
    record = perception.from_ocr(payload("image_ocr.json"), source_type="screenshot", source_path="a.png")
    assert consumer_errors(record, tmp_path) == []


def test_a_ui_record_satisfies_the_consumer(tmp_path):
    record = perception.from_ui(payload("analyze_ui.json"), source_path="ui.png")
    assert consumer_errors(record, tmp_path) == []


def test_an_architecture_record_satisfies_the_consumer(tmp_path):
    record = perception.from_architecture(payload("observe_architecture.json"))
    assert consumer_errors(record, tmp_path) == []


def test_a_broken_record_is_rejected_by_the_consumer(tmp_path):
    """The negative half. Without it a passing gate proves only that nothing
    was looked at — which is what the gate reports today, with no artifacts in
    the repo at all."""
    record = perception.from_ocr(payload("image_ocr.json"), source_type="screenshot", source_path="a.png")
    record["confidence"] = "very high"
    assert consumer_errors(record, tmp_path)


# ── source_type is mapped, never guessed ─────────────────────────────────────

def test_the_architecture_source_type_comes_from_the_producer():
    record = perception.from_architecture(payload("observe_architecture.json"))
    assert record["source_type"] == "diagram"


def test_the_ui_source_type_comes_from_the_producer():
    record = perception.from_ui(payload("analyze_ui.json"), source_path="ui.png")
    assert record["source_type"] == "ui"


def test_an_unmappable_source_type_is_refused():
    """A producer value with no place in the consumer's enum is an error, not
    an invitation to pick the closest one."""
    broken = {**payload("analyze_ui.json"), "screenshot_type": "hologram"}
    with pytest.raises(ValueError, match="source_type"):
        perception.from_ui(broken, source_path="ui.png")


def test_a_producer_that_says_unknown_defers_to_the_caller():
    """`unknown` is a real output of the UI classifier and is not a kind of
    image. The caller may say what it is; nothing here decides for them."""
    source = {**payload("analyze_ui.json"), "screenshot_type": "unknown"}
    with pytest.raises(ValueError, match="source_type"):
        perception.from_ui(source, source_path="ui.png")
    assert perception.from_ui(source, source_path="ui.png", source_type="screenshot")["source_type"] == "screenshot"


def test_a_dashboard_is_not_silently_called_something_else():
    """As defensible to call a ui as a screenshot. A coin toss recorded as an
    observation is worse than an error."""
    source = {**payload("observe_architecture.json"), "image_type": "dashboard"}
    with pytest.raises(ValueError, match="source_type"):
        perception.from_architecture(source)
    assert perception.from_architecture(source, source_type="ui")["source_type"] == "ui"


def test_a_producer_value_that_maps_is_not_overridden():
    """The producer observed it. A caller hint does not get to contradict it."""
    record = perception.from_architecture(
        payload("observe_architecture.json"), source_type="terminal"
    )
    assert record["source_type"] == "diagram"


def test_ocr_output_cannot_name_its_own_source_type():
    """image_ocr.v1 carries neither the kind of image nor its path. The caller
    supplies both, because the producer genuinely does not know them."""
    with pytest.raises(ValueError, match="source_type"):
        perception.from_ocr(payload("image_ocr.json"), source_type="hologram", source_path="a.png")


# ── confidence is about the record, not about a detection ────────────────────

@pytest.mark.parametrize(
    "ocr_text, regions, summary, available, expected",
    [
        ("",       [],          "",        True,  "low"),
        ("",       [],          "",        False, "low"),
        ("text",   [],          "",        True,  "medium"),
        ("text",   [{"a": 1}],  "",        False, "medium"),
        ("text",   [{"a": 1}],  "",        True,  "high"),
        ("text",   [{"a": 1}],  "summary", True,  "high"),
        ("",       [{"a": 1}],  "summary", True,  "high"),
    ],
)
def test_confidence_describes_how_complete_the_record_is(ocr_text, regions, summary, available, expected):
    assert perception.derive_confidence(
        ocr_text=ocr_text,
        detected_regions=regions,
        visual_summary=summary,
        capabilities_available=available,
    ) == expected


def test_per_region_confidence_keeps_its_own_meaning():
    """Two different questions that share a word. The float inside a region is
    the detector's certainty about that box; the record's confidence is not a
    claim about accuracy at all, and normalizing must not overwrite one with
    the other."""
    source = payload("image_ocr.json")
    source["regions"] = [{"text": "hi", "bbox": [0, 0, 1, 1], "confidence": 0.42}]
    source["full_text"] = "hi"
    source["ocr_available"] = True
    record = perception.from_ocr(source, source_type="screenshot", source_path="a.png")
    assert record["detected_regions"][0]["confidence"] == 0.42
    assert record["confidence"] in perception.CONFIDENCE_LEVELS


# ── nothing is invented ──────────────────────────────────────────────────────

def test_a_producer_with_no_text_reports_no_text():
    record = perception.from_ui(payload("analyze_ui.json"), source_path="ui.png")
    assert record["ocr_text"] == ""


def test_the_path_is_the_callers_not_a_guess():
    record = perception.from_ocr(payload("image_ocr.json"), source_type="terminal", source_path="/tmp/x.png")
    assert record["source_path"] == "/tmp/x.png"


def test_risk_signals_carry_the_producers_own_findings():
    source = payload("analyze_ui.json")
    source["issues"] = ["contrast below 4.5:1"]
    record = perception.from_ui(source, source_path="ui.png")
    assert record["risk_signals"] == ["contrast below 4.5:1"]


# ── v1.4 conventions survive normalization ───────────────────────────────────

def test_the_prompt_injection_warning_is_not_dropped():
    """Image-derived text is data. The warning travels with it or the record is
    less safe than what it was built from."""
    source = payload("image_ocr.json")
    record = perception.from_ocr(source, source_type="screenshot", source_path="a.png")
    assert any("must not be executed" in limitation for limitation in record["limitations"])


def test_every_record_declares_its_schema():
    for record in (
        perception.from_ocr(payload("image_ocr.json"), source_type="screenshot", source_path="a.png"),
        perception.from_ui(payload("analyze_ui.json"), source_path="ui.png"),
        perception.from_architecture(payload("observe_architecture.json")),
    ):
        assert record["schema_version"] == perception.SCHEMA_VERSION


def test_the_added_fields_do_not_disturb_the_consumer(tmp_path):
    """schema_version and limitations are this repo's additions on top of a
    contract someone else froze. The consumer checks required keys and does not
    reject unknown ones — pinned here so the addition stays safe."""
    record = perception.from_architecture(payload("observe_architecture.json"))
    assert "schema_version" in record and "limitations" in record
    assert consumer_errors(record, tmp_path) == []


# ── the shipped samples ──────────────────────────────────────────────────────

@pytest.mark.parametrize("name", ["ocr.json", "ui.json", "diagram.json"])
def test_every_shipped_sample_satisfies_the_consumer(name, tmp_path):
    """Samples are documentation that can go stale. These are checked against
    the same validator the gate uses, so they cannot drift quietly."""
    sample = json.loads((ROOT / "examples" / "perception" / name).read_text(encoding="utf-8"))
    assert consumer_errors(sample, tmp_path) == []


def test_the_samples_cover_the_producers_this_repo_has():
    kinds = {
        json.loads((ROOT / "examples" / "perception" / name).read_text(encoding="utf-8"))["source_type"]
        for name in ("ocr.json", "ui.json", "diagram.json")
    }
    assert kinds == {"screenshot", "ui", "diagram"}
