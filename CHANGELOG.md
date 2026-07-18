# Changelog

## Unreleased

### Changed

- `release-check.sh` now conforms to the `repo_release_check.v1` contract:
  `--json` emits the machine-readable verdict (`schema`, `repo`, `status`,
  `blockers`, `warnings`, `evidence`) on clean stdout and exits 0; `--dry-run`
  and `--json` skip the clean-tree requirement (the caller owns it). Human mode
  is unchanged. Lets mq-agent's `stack release --all --preflight` read the
  release verdict.

## 1.4.0 — 2026-06-03

### Added

- Stable MCP sample payloads for all seven read-only tools under
  `examples/mcp-payloads/`.
- `scripts/check-mcp-sample-payloads.py` contract/freshness check for sample
  payload keysets, schema fields, limitations and prompt-injection warnings.
- Release-check coverage for MCP sample payload freshness.
- mq-agent handoff examples for architecture-image and visual screenshot review.
- MQ workflow guidance for `local-fast`, `local-deep` and `cloud-verify`.

### Changed

- `docs/tool-safety.md` now lists the current read-only MCP tool surface.

### Fixed

- `mq-image` version lookup now uses the repo `VERSION` file in source checkouts
  and installed package metadata in wheel installs.
- Web `/analyze` now returns `422` validation errors for invalid `conf` and
  `vision_mode` values instead of surfacing internal server errors.

## 1.3.0 — 2026-06-01

### Added

- `mq_image_analyze/pipelines/ocr_pipeline.py` — standalone OCR pipeline returning
  `image_ocr.v1` schema: text regions with bbox and confidence, `full_text`
  concatenation, `ocr_available` flag, limitations. pytesseract optional —
  degrades gracefully. Prompt injection warning built into `limitations` field.
- `image_ocr` MCP tool in `mq_image_analyze/mcp/server.py` — wraps OCR pipeline;
  safety class A; read-only
- `tests/test_ocr.py` — 12 tests covering schema, safety, graceful degradation,
  MCP tool contract, error handling
- `examples/mq-agent-workflow.md` — workflow examples for architecture review, UI
  screenshot review, OCR extraction, image comparison

### Changed

- `docs/mcp-tools.md` — `image_ocr` promoted from "planned" to stable tool in contract table
- `docs/MQ_MCP_COMPATIBILITY.md` — `image_ocr` "(planned)" removed; `image_ocr.v1` schema noted
- `README.md` — tool count updated (six → seven); v1.3.0 added to roadmap table;
  proof block updated to 1.3.0

---

## 1.2.1 — 2026-06-01

### Added

- `docs/MQ_MCP_COMPATIBILITY.md` — dedicated compatibility doc: role boundary,
  safety rules for image-derived text, MCP tool contract table (implemented + planned),
  hard boundary, guide for consuming mq-image-analyze output in mq-mcp
- `docs/mcp-tools.md` — tool contract summary table added at top; planned `image_ocr`
  tool noted; link to MQ_MCP_COMPATIBILITY.md

### Changed

- README: `mq-mcp compatibility` section links to new MQ_MCP_COMPATIBILITY.md

---

## 1.2.0 — 2026-06-01

### Changed

- README: opening paragraph updated — "visual perception layer for the mq ecosystem";
  architecture flow diagram added; "mq-mcp compatibility" responsibility table added;
  "Hard boundary" section added (must/may contract)
- ROADMAP: release map table added; v1.2.0 section added
- `release-check.sh`: `mq-image mcp --help` and `python -m compileall` checks added

---

## 1.1.0 — 2026-05-28

### Added

- `visual_architecture_observation.v1` JSON schema — structured output for architecture
  diagrams, dashboards, and screenshots designed for mq-mcp consumption.
- `mq_image_analyze/vision/architecture/` module:
  - `observation.py` — `VisualArchitectureObservation`, `Component`, `Connection`,
    `Group`, `TextRegion`, `ArchLayout` dataclasses.
  - `classifier.py` — heuristic image type classification:
    `architecture-diagram | dashboard | terminal | ui-screenshot | unknown`.
  - `detector.py` — fill-based component detection (morphological opening removes
    thin connecting lines), connection direction detection, color-group clustering,
    dominant flow inference (`left-to-right | top-to-bottom | radial | unknown`).
- `mq_image_analyze/pipelines/architecture_pipeline.py` — full pipeline:
  classify → detect components → detect connections → detect groups → OCR (optional).
- `observe_architecture` MCP tool — produces `visual_architecture_observation.v1`
  JSON blob; OCR via pytesseract when installed (optional dependency).
- `docs/visual-architecture-schema.md` — full field reference, image type enum,
  OCR setup instructions, and mq-mcp integration pattern.
- `examples/architecture-observation.json` — example output with 4 components,
  3 connections, 2 groups.
- 15 new tests in `tests/test_architecture.py` covering classifier, detector,
  pipeline integration, and MCP tool serialization.

## 1.0.0 — 2026-05-25

### Added

- Stable CLI surface for `analyze`, `analyze-ui`, `compare`, `doctor`, `serve`, and `mcp`.
- Vision backend selection with `local-fast`, `local-deep`, and `cloud-verify`.
- OpenAI cloud verification adapter for GPT-4o/GPT-4.1 vision-capable models.
- Stable JSON output fields for semantic backend metadata: `vision_mode` and `vision_model`.
- MCP tool contracts for image analysis, palette extraction, reverse prompts, comparison, and UI analysis.
- Release workflow for version tags.

### Changed

- Updated README, CLI, JSON schema, MCP, roadmap, and release documentation for the 1.0 contract.
- Release checks now represent the stable toolkit readiness gate.

## 0.1.0 — 2026-05-25

### Added

- Project scaffold: vision/, reasoning/, mcp/, cli/, adapters/, pipelines/
- `vision/detection` — YOLOv8n object detection
- `vision/palette` — dominant color extraction, brightness/contrast labels
- `vision/composition` — rule-of-thirds, symmetry, visual weight, depth
- `reasoning/prompts/reverse_prompt` — structured reverse prompt builder
- `cli/analyze` — `mq-image analyze <image>` command with rich output and `--json`
- `pyproject.toml` with entry point `mq-image`
