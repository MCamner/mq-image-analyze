# Roadmap

## v0.1.0 — Vision Intelligence MVP — Done

- [x] Project scaffold (vision, reasoning, mcp, cli, adapters, pipelines)
- [x] `mq-image analyze <image>` CLI command
- [x] Rich terminal output
- [x] `--json` output mode
- [x] Object detection (YOLOv8n)
- [x] Palette extraction (dominant colors, brightness, contrast)
- [x] Composition heuristics (rule-of-thirds, symmetry, visual weight, depth)
- [x] Reverse prompt builder

## v0.1.1 — Hardening — Done

- [x] MIT LICENSE
- [x] Tests — palette, composition, CLI (13 passing)
- [x] GitHub Actions CI (Python 3.11 / 3.12)
- [x] docs/architecture.md
- [x] docs/mcp-tools.md
- [x] examples/sample-analysis.json
- [x] `mq-image --version`
- [x] `mq-image doctor`
- [x] `mq-image analyze --exhaustive --conf` (high-recall mode)
- [x] JSON schema contract doc (`docs/json-schema.md`)
- [x] scripts/validate.sh
- [x] release-check.sh
- [x] No Silent Omission Rule in MCP docs
- [x] `limitations` field in all JSON output
- [x] Fallback behavior when model file is missing
- [x] Vision backend selection: `local-fast`, `local-deep`, `cloud-verify`

## v0.2.0 — Image Comparison — Done

- [x] `mq-image compare before.jpg after.jpg`
- [x] Style drift score
- [x] Composition difference
- [x] Palette difference
- [x] AI-look detection baseline

## v0.3.0 — Screenshot Intelligence — Done

- [x] `mq-image analyze-ui screenshot.png`
- [x] UI layout detection (contour-based region classification)
- [x] Hierarchy / spacing / contrast review (WCAG contrast ratio, hierarchy depth, grid alignment)
- [x] Terminal screenshot analysis (dark + monochrome + text density heuristic)
- [x] GitHub README screenshot analysis (light + tall + text density heuristic)

## v0.4.0 — MCP Integration — Done

- [x] MCP server (`mq_image_analyze/mcp/server.py`) using FastMCP
- [x] `analyze_image` tool
- [x] `extract_palette` tool
- [x] `reverse_prompt` tool
- [x] `compare_images` tool
- [x] `analyze_ui` tool
- [x] Tool safety classification (all tools: safe / read-only)
- [x] `mq-image mcp` CLI command (stdio + sse transport)
- [x] `[mcp]` optional dependency group in pyproject.toml

## v0.5.0 — MQ Ecosystem Integration — Done

- [x] mq-agent skill integration (`skills/visual-analysis/SKILL.md` in mq-agent)
- [x] mqlaunch bridge (`scripts/mqlaunch-bridge.sh`)
- [x] repo-signal readiness profile (`repo-signal.yml`)
- [x] GitHub Pages docs (`docs/index.md` + `docs/_config.yml`)
- [x] Examples generated in CI (`.github/workflows/examples.yml`)

## v1.0.0 — Stable Visual Reasoning Toolkit — Done

- [x] Stable CLI surface
- [x] Stable JSON schemas
- [x] Stable MCP tool contracts
- [x] Full documentation
- [x] Release workflow
