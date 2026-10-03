# Roadmap

## Release map

| Version | Theme | Status |
| ------- | ----- | ------ |
| v0.1.0 | Vision Intelligence MVP | Done |
| v0.1.1 | Hardening | Done |
| v0.2.0 | Image Comparison | Done |
| v0.3.0 | Screenshot Intelligence | Done |
| v0.4.0 | MCP Integration | Done |
| v0.5.0 | MQ Ecosystem Integration | Done |
| v1.0.0 | Stable Visual Reasoning Toolkit | Done |
| v1.1.0 | Visual cognition for architecture review | Done |
| v1.2.0 | mq-mcp compatibility docs + hard boundary | Done |
| v1.2.1 | `MQ_MCP_COMPATIBILITY.md` + MCP tool contract table | Done |
| v1.3.0 | `image_ocr` MCP tool + mq-agent workflow examples | Done |
| v1.4.0 | Perception workflow integration hardening | Done |
| v1.5.0 | Normalized perception contract for Release Gate v2 | Done |
| v1.6.0 | Runnable perception contract | Done |
| v1.7.0 | Safer agent and cloud use, CI-ready comparison | Done |
| v1.8.0 | Screenshot regression for the Release Gate | Done |

---

## v1.8.0 — Screenshot regression for the Release Gate — Done

Goal:

Turn a directory of screenshots into release evidence: what changed, where,
and a CI exit code that stops the release when a screen changed or vanished.

- [x] `mq-image regress <baseline> <current>`, paired by file name
- [x] Threshold on the share of changed pixels, with a noise filter; default is
  any real change
- [x] Changed regions as boxes, overlays, side-by-side HTML report, JSONL
- [x] One `perception.v1` artifact per failing screen, checked against mq-mcp's
  validator
- [x] `--ignore-region` for clocks, dates and other dynamic content
- [x] `--update-baseline`

Not in this release:

- Blocking in the Release Gate itself. mq-mcp treats perception risk as
  advisory; `regress` blocks through its exit code.
- Judging whether a change was intended. This is pixel comparison.

---

## v1.7.0 — Safer agent and cloud use, CI-ready comparison — Done

Goal:

Limit what an agent can make the MCP server read and what leaves the machine
in cloud-verify, and make the CLI usable in CI and on screenshot series.

- [x] `MQ_IMAGE_ALLOWED_ROOTS` path confinement for every MCP tool
- [x] `compare`: `pixel_diff`, `size_changed`, `--fail-over` exit code
- [x] Opt-in, fail-closed redaction of personnummer and email before cloud-verify
- [x] `mq-image analyze <directory>` with JSONL output
- [x] `--cache` for semantic captions (CLI only; MCP stays write-free)

Not in this release:

- Name redaction. Names are not pattern-shaped; that needs a name list or an
  NER model and is a separate decision.
- A full `uv lock` refresh with uv 0.12 (it rewrites CUDA platform markers).

---

## v1.6.0 — Runnable perception contract — Done

Goal:

v1.5 defined `perception.v1`, but only the test suite could produce it. Make
the artifact producible from an image, and remove surface that claimed more
than the code does.

- [x] `mq-image perceive <image> --producer ui|architecture|ocr` with `--out`
- [x] `image_perception` MCP tool, sample payload validated by mq-mcp's own
  perception validator
- [x] `mq-image ocr`, CLI parity with the `image_ocr` MCP tool
- [x] Remove 17 empty stub packages and the stale root `web/` copy; docs list
  only modules that exist
- [x] Validate web uploads: extension, byte size, pixel count, readability

Not in this release:

- No new analysis. `perceive` runs existing producers and existing normalizers.
- `mq-agent review perception <image>` is still mq-agent's work.

---

## v1.5.0 — Normalized perception contract for Release Gate v2 — Done

Goal:

Make mq-image-analyze output easy for mq-agent and mq-mcp Release Gate v2 to
consume in repeatable screenshot, OCR, UI and diagram review workflows.

Normalized perception object:

```json
{
  "source_type": "screenshot | diagram | ui | terminal | browser",
  "source_path": "path/to/image.png",
  "ocr_text": "...",
  "visual_summary": "...",
  "detected_regions": [],
  "risk_signals": [],
  "confidence": "low | medium | high"
}
```

Scope:

- [x] Document the normalized perception object and compatibility rules
  (`docs/MQ_MCP_COMPATIBILITY.md`)
- [x] Add stable sample payloads for screenshot, diagram, UI and OCR outputs
  (`examples/perception/`, one per producer, each checked against the consumer)
- [x] Add `sample_perception_output.json` fixture for cross-repo validation
- [x] Keep prompt-injection warnings and `limitations` in image-derived text
- [x] Add OCR fallback and confidence handling tests
- [x] Prove `perception.v1` compatibility against mq-mcp's real Release Gate
  validator, with a positive fixture and a negative one that must block —
  imported from the sibling checkout rather than restated here
- [x] Document the implemented flow: mq-image-analyze → `perception.v1`
  artifact → mq-mcp Release Gate v2 and read-only perception review tools

Follow-up, owned elsewhere:

- [ ] Add an mq-agent perception workflow/command
  (**Owner: mq-agent.** `mq-agent review` offers `file`, `diff` and `repo`;
  there is no perception command. Not a blocker for this producer contract.)

Not in this release, and deliberately:

- No new analysis. Normalization renames, joins and restates what the pipelines
  already produce; nothing is measured or inferred during it.
- `mq-agent review perception <image>` is mq-agent's work, not this repo's.
  Until it exists the chain is mq-image-analyze → artifact → mq-mcp gate.

Scope status:

```text
v1.5 producer contract    done
mq-mcp compatibility      done, proven against the real validator
mq-agent orchestration    deferred to mq-agent
```

One principle worth keeping from this release: **a green gate is not evidence
until it evaluated something.** Before this release mq-mcp's perception check
answered `No perception artifacts found; nothing to validate` — a pass
indistinguishable from a real validation. A no-op pass may never be cited as
compatibility evidence; that is why the negative fixture is part of the proof.

Boundary:

```text
mq-image-analyze owns visual extraction.
mq-agent owns routing and operator workflow.
mq-mcp owns deterministic review and release validation.
```

Non-goals:

- no review generation
- no release gate rule engine
- no semantic memory ownership
- no write-capable MCP tools

---

## v1.4.0 — Perception workflow integration hardening — Done

Goal:

Make mq-image-analyze easier for mq-agent and mq-mcp to consume in repeatable
review workflows.

Planned scope:

- [x] Add canonical examples for UI review, OCR review and architecture observation
- [x] Add stable sample payloads for every MCP tool
- [x] Add contract checks for `limitations`, `schema_version` and prompt-injection warnings
- [x] Add mq-agent handoff examples for screenshot review and diagram review
- [x] Add release-check coverage for example payload freshness
- [x] Document when to use `local-fast`, `local-deep` and `cloud-verify` in MQ workflows

Non-goals:

- No autonomous visual agent
- No write-capable MCP tools
- No semantic memory ownership

---

## v1.3.0 — `image_ocr` MCP tool + mq-agent workflow examples — Done

- [x] Standalone `image_ocr` MCP tool — `image_ocr.v1` schema with text regions,
  bbox, confidence, full_text, ocr_available, limitations
- [x] `mq_image_analyze/pipelines/ocr_pipeline.py` — reusable OCR pipeline;
  pytesseract optional; prompt injection warning in every limitations field
- [x] 12 tests in `tests/test_ocr.py`
- [x] `examples/mq-agent-workflow.md` — architecture review, UI review, OCR, comparison
- [x] `docs/mcp-tools.md` — `image_ocr` promoted from planned to stable
- [x] `docs/MQ_MCP_COMPATIBILITY.md` — `image_ocr` "(planned)" removed; v1 schema noted
- [x] All 7 MCP tools validated in CI

---

## v1.2.1 — `MQ_MCP_COMPATIBILITY.md` + MCP tool contract table — Done

- [x] `docs/MQ_MCP_COMPATIBILITY.md` — role boundary, safety rules for image-derived text,
  MCP tool contract table, hard boundary, consumption guide for mq-mcp
- [x] `docs/mcp-tools.md` — contract summary table added; planned `image_ocr` documented
- [x] README — `mq-mcp compatibility` section links to `MQ_MCP_COMPATIBILITY.md`

---

## v1.2.0 — mq-mcp compatibility docs + hard boundary — Done

- [x] README: opening updated to "visual perception layer for the mq ecosystem"
- [x] README: architecture flow diagram added
- [x] README: `mq-mcp compatibility` section with responsibility table
- [x] README: `Hard boundary` section — must/may contract
- [x] ROADMAP: release map table added
- [x] ROADMAP: v1.2.0 section
- [x] `release-check.sh`: `mq-image mcp --help` check added
- [x] `release-check.sh`: `compileall` check added

Non-goals:

- No new MCP tools
- No new pipelines
- No changes to JSON schemas

---

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

## v1.1.0 — Visual cognition for architecture review — Done

Goal:

Make mq-image-analyze the visual cognition layer for the mq ecosystem while
leaving review generation and architecture reasoning to mq-mcp.

- [x] Add `visual_architecture_observation.v1` JSON schema optimized for mq-mcp consumption
- [x] Add heuristic topology extraction: component boxes, connection lines, color groups, flow direction
- [x] Add OCR pipeline (pytesseract optional) for text extraction from diagram boxes
- [x] Add `observe_architecture` MCP tool
- [x] Add `docs/visual-architecture-schema.md` with full field reference and integration pattern
- [x] Add `examples/architecture-observation.json` example output
- [x] 15 tests covering classifier, detector, pipeline, and MCP tool serialization

Non-goals (unchanged):

- No review generation
- No semantic memory runtime
- No architecture decision engine

---
