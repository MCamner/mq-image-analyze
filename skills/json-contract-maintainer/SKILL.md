---
name: json-contract-maintainer
description: Use when changing mq-image-analyze JSON output schemas, analysis result fields, compare output, UI analysis output, exhaustive mode, or stable integration contracts.
---

# JSON Contract Maintainer

Use this skill for any machine-readable output change.

## Evals

### Should trigger

- "add a field to the analyze JSON output"
- "change the compare output schema"
- "stabilize the UI analysis contract"
- "version the exhaustive-mode output"

### Should not trigger

- "change a CLI flag" → use `cli-maintainer`
- "change MCP tool schemas" → use `mcp-tools-maintainer`
- "update schema docs only" → use `docs-maintainer`

## Core Files

- `docs/json-schema.md`
- `docs/mcp-tools.md`
- `examples/sample-analysis.json`
- `examples/generated/*.json`
- `mq_image_analyze/cli/analyze.py`
- `mq_image_analyze/cli/compare.py`
- `mq_image_analyze/cli/analyze_ui.py`
- `mq_image_analyze/reasoning/comparison/comparator.py`
- `mq_image_analyze/vision/ui/analyzer.py`
- `tests/test_json_schema.py`
- `tests/test_compare.py`
- `tests/test_analyze_ui.py`
- `tests/test_exhaustive.py`

## Stability Rules

- Current schema version: `mq-image.analysis.v1`.
- Additive fields are allowed in minor versions.
- Field removal or incompatible type changes require a major version bump.
- `limitations` must always be present in full analysis outputs.
- Summary mode may dedupe; exhaustive mode must preserve raw detections.
- JSON output must not include ANSI text or human-only formatting.

## Change Workflow

1. Update implementation.
2. Update tests for expected fields and modes.
3. Update `docs/json-schema.md`.
4. Regenerate or update examples when output shape changes.
5. Update MCP docs if tool responses change.

## Verification

```bash
python -m pytest \
  tests/test_json_schema.py \
  tests/test_compare.py \
  tests/test_analyze_ui.py \
  tests/test_exhaustive.py \
  -q
```

Before release:

```bash
bash scripts/validate.sh
```
