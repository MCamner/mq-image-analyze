# Changelog

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
