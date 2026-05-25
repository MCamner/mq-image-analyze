---
name: repo-aware
description: Use when inspecting, explaining, planning, reviewing, or changing mq-image-analyze with repository-specific context.
---

# Repo Aware

Use this skill to ground work in mq-image-analyze's actual architecture,
contracts, tests, and release flow.

## What This Repo Is

mq-image-analyze is the visual perception layer for the MQ ecosystem. It
analyzes images, screenshots, composition, palettes, UI structure, reverse
prompts, and visual differences through CLI, web, and MCP surfaces.

Primary surfaces:

- `mq_image_analyze/vision/` for object, palette, composition, UI, semantic,
  content, OCR, and metadata pipelines
- `mq_image_analyze/reasoning/` for prompts, comparisons, UI analysis, scoring,
  and cinematic/style reasoning
- `mq_image_analyze/cli/` for `mq-image` commands
- `mq_image_analyze/mcp/` for MCP server and tool contracts
- `mq_image_analyze/web/` and `web/` for the web UI/server package
- `docs/` for architecture, CLI, JSON schema, MCP tools, safety, model setup,
  integration, and release docs
- `skills/` for agent-facing visual reasoning skills
- `tests/` for CLI, schema, MCP, web package, provider, composition, palette,
  comparison, and safety coverage

## First Inspection

Start with:

```bash
git status --short
rg --files
sed -n '1,220p' README.md
sed -n '1,220p' pyproject.toml
sed -n '1,220p' docs/architecture.md
```

For behavior changes, inspect the matching CLI, pipeline, docs, and tests.

## Verification

Use focused checks when possible:

```bash
python -m compileall mq_image_analyze -q
python -m pytest -q
bash scripts/validate.sh
```

For release-critical changes:

```bash
bash release-check.sh
```

## Guardrails

- Preserve stable JSON contracts unless intentionally versioning a breaking
  change.
- No model weights, `.env`, or credentials in git.
- Keep visual tools read-only by default.
- Do not silently omit detections in exhaustive mode.
- Update docs and tests whenever CLI, MCP, JSON, or skill behavior changes.
