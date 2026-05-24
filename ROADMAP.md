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

## v0.1.1 — Hardening — In progress

- [x] MIT LICENSE
- [x] Tests — palette, composition, CLI (13 passing)
- [x] GitHub Actions CI (Python 3.11 / 3.12)
- [x] docs/architecture.md
- [x] docs/mcp-tools.md
- [x] examples/sample-analysis.json
- [ ] `mq-image --version`
- [ ] `mq-image doctor`
- [ ] Fallback behavior when model file is missing
- [ ] JSON schema contract doc
- [ ] scripts/validate.sh
- [ ] release-check.sh

## v0.2.0 — Image Comparison — Planned

- [ ] `mq-image compare before.jpg after.jpg`
- [ ] Style drift score
- [ ] Composition difference
- [ ] Palette difference
- [ ] AI-look detection baseline

## v0.3.0 — Screenshot Intelligence — Planned

- [ ] `mq-image analyze-ui screenshot.png`
- [ ] UI layout detection
- [ ] Hierarchy / spacing / contrast review
- [ ] Terminal screenshot analysis
- [ ] GitHub README screenshot analysis

## v0.4.0 — MCP Integration — Planned

- [ ] MCP server (`mq_image_analyze/mcp/server.py`)
- [ ] `analyze_image` tool
- [ ] `extract_palette` tool
- [ ] `reverse_prompt` tool
- [ ] `compare_images` tool
- [ ] `analyze_ui` tool
- [ ] Tool safety classification

## v0.5.0 — MQ Ecosystem Integration — Planned

- [ ] mq-agent skill integration
- [ ] mqlaunch bridge
- [ ] repo-signal readiness profile
- [ ] GitHub Pages docs
- [ ] Examples generated in CI

## v1.0.0 — Stable Visual Reasoning Toolkit — Future

- [ ] Stable CLI surface
- [ ] Stable JSON schemas
- [ ] Stable MCP tool contracts
- [ ] Full documentation
- [ ] Release workflow
