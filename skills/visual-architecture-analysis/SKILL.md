---
name: visual-architecture-analysis
description: Use when adding or changing mq-image-analyze features for architecture diagrams, infrastructure topology screenshots, terminal screenshots, OCR pipelines, or visual observations consumed by mq-mcp.
---

# Visual Architecture Analysis

Use this skill when visual analysis feeds architecture or review workflows.

## Boundary

mq-image-analyze owns visual observation: objects, layout, OCR, topology hints, palette, screenshot structure and machine-readable visual facts.

It must not generate final review findings, own architecture memory, or make architecture decisions. mq-mcp consumes the observations and performs cognition.

## Files To Inspect

- `mq_image_analyze/cli/`
- `mq_image_analyze/vision/`
- `mq_image_analyze/reasoning/`
- `docs/json-schema.md`
- `docs/mcp-tools.md`
- `examples/`
- `tests/test_analyze_ui.py`
- `tests/test_json_schema.py`

## Output Rules

- Prefer structured JSON observations over prose.
- Include limitations and confidence where detection is heuristic.
- Keep OCR text bounded and avoid claiming certainty for low-quality images.
- Add schema fields additively unless a major version bump is intended.

## Verification

```bash
python -m pytest tests/test_json_schema.py tests/test_analyze_ui.py -q
bash scripts/validate.sh
```

Update examples when JSON output changes.
