"""One shape for what this repo saw, for the tools that consume it.

Every pipeline here already reports what it found, and each reports it in its
own words: `screenshot_type` or `image_type`, `full_text` or `text_regions`,
`semantic_caption` or `prompt`, `issues` or nothing at all. That is fine inside
a pipeline and useless across a repository boundary, where a consumer has to
know one shape rather than five.

The shape is not chosen here. mq-mcp's Release Gate v2 already validates
perception artifacts and blocks a release on an invalid one, so the required
fields, the `source_type` vocabulary and the `confidence` vocabulary were
frozen by the consumer. This module's job is to satisfy that contract from
what the pipelines already produce, and to add `schema_version` and
`limitations` on top — this repo's conventions since v1.4, and additive because
the consumer checks the keys it requires without rejecting the ones it does not.

**No new perception happens here.** Nothing is measured, classified or
inferred: every field is a rename, a join, or a restatement of counts the
producer already established. Where a producer genuinely does not know
something — an OCR run knows neither the kind of image nor its path — the
caller supplies it, and where a producer's own vocabulary has no honest home in
the consumer's, this refuses rather than picking the closest one.
"""
from __future__ import annotations

from typing import Any

#: This repo's addition, on top of the consumer's required fields.
SCHEMA_VERSION = "perception.v1"

#: Frozen by mq-mcp's release gate. Not extendable from this side.
SOURCE_TYPES = frozenset({"screenshot", "diagram", "ui", "terminal", "browser"})
CONFIDENCE_LEVELS = ("low", "medium", "high")

#: Producer vocabulary → consumer vocabulary. Only unambiguous pairs appear.
#: `unknown` is absent because it is not a kind of image, and `dashboard`
#: because it is as defensible to call it a ui as a screenshot — a coin toss
#: recorded as an observation is worse than asking the caller.
_UI_SOURCE_TYPES = {
    "terminal": "terminal",
    "browser": "browser",
    "app-ui": "ui",
    "readme": "screenshot",
}
_ARCHITECTURE_SOURCE_TYPES = {
    "architecture-diagram": "diagram",
    "terminal": "terminal",
    "ui-screenshot": "ui",
}


def _resolve_source_type(producer_value: Any, mapping: dict[str, str], fallback: str | None) -> str:
    """The producer's word, translated — or the caller's, when it has none."""
    mapped = mapping.get(str(producer_value))
    if mapped is not None:
        return mapped
    if fallback is not None:
        return _checked_source_type(fallback)
    raise ValueError(
        f"source_type {producer_value!r} has no equivalent in {sorted(SOURCE_TYPES)}; "
        "pass source_type explicitly rather than letting it be guessed"
    )


def _checked_source_type(value: Any) -> str:
    if value not in SOURCE_TYPES:
        raise ValueError(f"source_type must be one of {sorted(SOURCE_TYPES)}, got {value!r}")
    return str(value)


def derive_confidence(
    *,
    ocr_text: str,
    detected_regions: list,
    visual_summary: str,
    capabilities_available: bool,
) -> str:
    """How complete this record is — not how sure anything in it is.

    The word is already taken inside this repo: a region carries the detector's
    certainty about one box, as a float. The consumer asks a different question
    with the same word, and conflating them would let a confident detection of
    one word in an otherwise empty image read as a confident perception record.

    Derived, never asserted, and only from what the producer already reported:
    how many of the three content fields carry anything, and whether the
    producer said a capability it has was unavailable.
    """
    filled = sum(bool(x) for x in (ocr_text, detected_regions, visual_summary))
    if filled == 0:
        return "low"
    if capabilities_available and filled >= 2:
        return "high"
    return "medium"


def _record(
    *,
    source_type: str,
    source_path: str,
    ocr_text: str,
    visual_summary: str,
    detected_regions: list,
    risk_signals: list,
    limitations: list,
    capabilities_available: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_type": source_type,
        "source_path": source_path,
        "ocr_text": ocr_text,
        "visual_summary": visual_summary,
        "detected_regions": list(detected_regions),
        "risk_signals": list(risk_signals),
        "confidence": derive_confidence(
            ocr_text=ocr_text,
            detected_regions=detected_regions,
            visual_summary=visual_summary,
            capabilities_available=capabilities_available,
        ),
        "limitations": list(limitations),
    }


def from_ocr(payload: dict[str, Any], *, source_type: str, source_path: str) -> dict[str, Any]:
    """Normalize an `image_ocr.v1` payload.

    OCR output names neither the kind of image nor where it came from, so both
    arrive from the caller. `visual_summary` stays empty: an OCR run looked at
    text and has nothing to say about the picture.
    """
    return _record(
        source_type=_checked_source_type(source_type),
        source_path=source_path,
        ocr_text=str(payload.get("full_text", "")),
        visual_summary="",
        detected_regions=payload.get("regions") or [],
        risk_signals=[],
        limitations=payload.get("limitations") or [],
        capabilities_available=bool(payload.get("ocr_available", False)),
    )


def from_ui(
    payload: dict[str, Any], *, source_path: str, source_type: str | None = None
) -> dict[str, Any]:
    """Normalize an `analyze_ui` payload.

    The accessibility `issues` the analyzer already found are the risk signals;
    nothing is re-judged here. The UI path performs no OCR, so `ocr_text` is
    empty rather than absent — the consumer requires the key, and an empty
    string is the true answer.
    """
    summary = payload.get("semantic_caption") or payload.get("prompt") or ""
    return _record(
        source_type=_resolve_source_type(
            payload.get("screenshot_type"), _UI_SOURCE_TYPES, source_type
        ),
        source_path=source_path,
        ocr_text="",
        visual_summary=str(summary),
        detected_regions=payload.get("layout_regions") or [],
        risk_signals=payload.get("issues") or [],
        limitations=payload.get("limitations") or [],
        capabilities_available=True,
    )


def _architecture_summary(payload: dict[str, Any]) -> str:
    """Counts the observation already established, stated in one line."""
    layout = payload.get("layout") or {}
    components = layout.get("component_count", len(payload.get("components") or []))
    connections = layout.get("connection_count", len(payload.get("connections") or []))
    groups = len(payload.get("groups") or [])
    return f"{components} component(s), {connections} connection(s), {groups} group(s)"


def from_architecture(
    payload: dict[str, Any], *, source_path: str | None = None, source_type: str | None = None
) -> dict[str, Any]:
    """Normalize a `visual_architecture_observation.v1` payload.

    This producer knows its own path and image type, so both default to what it
    reported. `ocr_text` is joined from the text regions it already extracted.
    """
    regions = payload.get("text_regions") or []
    text = " ".join(
        r.get("text", "") if isinstance(r, dict) else str(r) for r in regions
    ).strip()
    return _record(
        source_type=_resolve_source_type(
            payload.get("image_type"), _ARCHITECTURE_SOURCE_TYPES, source_type
        ),
        source_path=str(source_path if source_path is not None else payload.get("image_path", "")),
        ocr_text=text,
        visual_summary=_architecture_summary(payload),
        detected_regions=payload.get("components") or [],
        risk_signals=[],
        limitations=payload.get("limitations") or [],
        capabilities_available=bool(payload.get("ocr_available", False)),
    )
