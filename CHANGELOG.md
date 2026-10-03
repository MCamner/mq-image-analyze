# Changelog

## Unreleased

### Added

- `mq-image regress <baseline> <current>`: visual regression for a directory of
  screenshots, paired by file name. Each screen is `unchanged`, `changed`,
  `missing` or `new`, with the boxes where pixels changed. Exit 1 when a screen
  changed or disappeared. `--out` writes `report.jsonl`, a side-by-side
  `report.html`, overlays with changed regions outlined, and one `perception.v1`
  artifact per failing screen for mq-mcp's Release Gate. `--update-baseline`
  copies the current run into the baseline. `--ignore-region [name:]x1,y1,x2,y2`
  excludes dynamic content such as clocks from every screen or from one.
- `perception.from_regression()`, checked against mq-mcp's own validator.

### Notes

- The threshold is the share of changed pixels, defaulting to any change that
  survives noise filtering. The first version thresholded the mean
  `pixel_diff`; a real run showed a renamed button scoring 0.001 and passing.
- mq-mcp's Release Gate lists the artifacts' risk signals as a warning and does
  not block on them. The `regress` exit code is what blocks CI.

## 1.7.0 — 2026-10-03

### Added

- `MQ_IMAGE_ALLOWED_ROOTS` confines every MCP tool to the listed directories.
  Paths are resolved first, so `..` and symlinks cannot escape, and the refusal
  comes before the existence check. Unset keeps the previous behavior.
- `compare` reports `pixel_diff` (mean absolute grayscale difference, 0–1) and
  `size_changed`. `--fail-over N` exits 1 when `pixel_diff` exceeds `N`, for
  visual regression in CI. Both fields are additive.
- Opt-in redaction before `cloud-verify`: `--redact`, `redact=True` on
  `analyze_image` and `reverse_prompt`, or `MQ_IMAGE_REDACT_CLOUD=1`. OCR-found
  personnummer and email addresses are painted black on the copy that is sent.
  Without OCR the image is not sent. Only OCR-readable text is covered.
- `mq-image analyze <directory>`: every image directly in it, JSONL with
  `--json`, `{path, error}` for a failing image, exit 1 if any failed.
- `mq-image analyze --cache`: semantic captions cached on disk, keyed on image
  bytes, vision mode, model, redaction and prompt text. MCP does not cache.

### Changed

- The accepted image extensions live in `mq_image_analyze/formats.py`, shared
  by CLI, MCP and web.
- `uv.lock` records the project version as 1.6.0. A full `uv lock` with uv 0.12
  also rewrites platform markers on CUDA dependencies and was left out.

## 1.6.0 — 2026-10-03

### Added

- `mq-image perceive <image> --producer ui|architecture|ocr` and the
  `image_perception` MCP tool. `perception.v1` existed only as normalizers fed
  by tests; there was no way to produce a Release Gate artifact from an image.
  `perception.perceive()` runs the named producer and hands its payload to the
  existing normalizer, so the map-or-refuse rule for `source_type` is
  unchanged. `--out` writes the artifact to a file.
- `mq-image ocr`, the CLI counterpart of the `image_ocr` MCP tool.
- `examples/mcp-payloads/image_perception.json`, covered by the sample payload
  check and by mq-mcp's own perception validator.

### Removed

- Seventeen packages that held nothing but an empty `__init__.py`:
  `adapters/` (flux, imagesorcery, openai, photoshop, sdxl), `mcp/schemas`,
  `mcp/tools`, `reasoning/{cinematic,comparisons,scoring,styles,ui_analysis}`,
  `utils`, and `vision/{metadata,ocr,screenshot,segmentation}`. Nothing
  imported them; the architecture doc and README described them as working
  features. Both now list only modules that exist.
- The root `web/` copy of the web server. `mq-image serve` has always run the
  packaged `mq_image_analyze/web/`; the root copy was an older version that
  lacked the vision-mode and `conf` validation.

### Fixed

- `POST /analyze` validates uploads before writing them to disk: extensions
  must match the MCP tools' set (415 otherwise), uploads are capped at 25 MB
  and decoded images at 50 million pixels (413), and bytes Pillow cannot read
  are refused (422). Previously any file of any size was written to a temp
  file and handed to the pipelines. An upload without a filename is now
  refused instead of being assumed to be a JPEG.

- `release-check.sh` runs markdownlint, which CI enforces as its own required
  workflow. Without it a local release check could report "Ready to tag" on a
  tree CI would reject, which is what happened during v1.5.0. No globs are
  passed, so the local run reads `.markdownlint-cli2.jsonc` exactly as the
  action does; an unrunnable linter is a failure rather than a pass.

## 1.5.0 — 2026-09-14

Normalized perception contract for Release Gate v2. The seventeen commits
since 1.4.0 are all in this release; the previous `Unreleased` section
described one of them, so this is rebuilt from the history rather than
renamed over.

### Added

- `mq_image_analyze.perception` — one normalized record, `perception.v1`, from
  any of the repo's producers. `from_ocr`, `from_ui` and `from_architecture`
  rename, join and restate what the pipelines already report; no perception
  happens during normalization.
- `tests/fixtures/sample_perception_output.json` — the cross-repo fixture, in
  a directory mq-mcp's Release Gate already globs.
- `examples/perception/` — one normalized sample per producer.
- Contract tests that run mq-mcp's own `_validate_perception_artifact` against
  what this repo produces, imported from the sibling checkout rather than
  restated. Skips when no mq-mcp checkout is present, so drift is reported as
  unverified rather than assumed absent. A negative fixture must block.
- The normalized perception record, its ownership split and its compatibility
  rules in `docs/MQ_MCP_COMPATIBILITY.md`.
- `.mq/repo-contract.json` for the MQ stack contract gate.
- Evals for all 13 skills, `scripts/check-skills.sh` and its CI job, plus a
  generated `SKILLS.md`.
- A Mermaid architecture diagram (#8) and a repo issue template.

### Changed

- `release-check.sh` now conforms to the `repo_release_check.v1` contract (#11):
  `--json` emits the machine-readable verdict (`schema`, `repo`, `status`,
  `blockers`, `warnings`, `evidence`) on clean stdout and exits 0; `--dry-run`
  and `--json` skip the clean-tree requirement (the caller owns it). Human mode
  is unchanged. Lets mq-agent's `stack release --all --preflight` read the
  release verdict.
- Markdown consistency is enforced in CI (#9).
- Agent scaffolding converged onto main (#10); `release_mode` declared direct;
  the MCP 1.x compatibility boundary declared in the repo contract.

### Fixed

- `mcp` constrained to the compatible 1.x API (#12).
- Local skills are discoverable by both Codex and Claude Code; `check-skills.sh`
  path resolution hardened for skill-local assets and bare directory mentions.

### Notes

- `confidence` on a perception record describes how complete the record is, not
  how certain any detection is. The per-region float inside `detected_regions`
  keeps its own meaning.
- An mq-agent perception command is deferred to mq-agent and is not part of
  this producer contract.
- A green gate is not evidence until it evaluated something: before this
  release mq-mcp's perception check answered `No perception artifacts found;
  nothing to validate`, which passes without looking at anything.

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
