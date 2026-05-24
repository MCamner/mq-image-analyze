# Changelog

## 0.1.0 — 2026-05-25

### Added

- Project scaffold: vision/, reasoning/, mcp/, cli/, adapters/, pipelines/
- `vision/detection` — YOLOv8n object detection
- `vision/palette` — dominant color extraction, brightness/contrast labels
- `vision/composition` — rule-of-thirds, symmetry, visual weight, depth
- `reasoning/prompts/reverse_prompt` — structured reverse prompt builder
- `cli/analyze` — `mq-image analyze <image>` command with rich output and `--json`
- `pyproject.toml` with entry point `mq-image`
