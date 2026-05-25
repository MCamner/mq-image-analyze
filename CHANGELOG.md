# Changelog

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
