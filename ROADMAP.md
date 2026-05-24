# Roadmap

## Phase 1 — Vision Intelligence MVP

- [x] Repository scaffold
- [x] `mq-image analyze <file>` CLI command
- [x] JSON output mode (`--json`)
- [x] Palette extraction (dominant colors, brightness, contrast)
- [x] Object detection (YOLOv8n)
- [x] Composition heuristics (rule-of-thirds, symmetry, visual weight, depth)
- [x] Reverse prompt generator
- [ ] Example image fixtures
- [ ] Test suite
- [ ] GitHub Actions CI
- [ ] `docs/architecture.md`
- [ ] `docs/mcp-tools.md`
- [ ] First release `v0.1.0`

## Phase 2 — Visual Reasoning

- [ ] `mq-image compare a.jpg b.jpg`
- [ ] `mq-image score image.jpg`
- [ ] Composition scoring with numeric output
- [ ] Cinematic analysis (lighting style, color grading)
- [ ] Style drift detection
- [ ] AI-look detection heuristics

## Phase 3 — Screenshot Intelligence

- [ ] `mq-image analyze-ui screenshot.png`
- [ ] UI layout extraction
- [ ] Design language detection
- [ ] Accessibility heuristics
- [ ] UI description generator
- [ ] Integration with mq-agent

## Phase 4 — Generation (optional)

Generation is secondary and will never dominate the product.

- [ ] Style transfer pipeline
- [ ] `mq-image transform image.jpg --style cinematic`
- [ ] Adapter integrations (SDXL, Flux)
