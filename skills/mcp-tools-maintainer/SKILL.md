---
name: mcp-tools-maintainer
description: Use when changing mq-image-analyze MCP server, MCP tool schemas, tool safety, read-only behavior, or mq-mcp/mq-agent integration.
---

# MCP Tools Maintainer

Use this skill for MCP behavior and tool contracts.

## Evals

### Should trigger

- "add an MCP tool to the image server"
- "tighten MCP tool read-only safety"
- "fix mq-mcp integration of the image tools"
- "the MCP tool schema is wrong"

### Should not trigger

- "change a CLI flag" → use `cli-maintainer`
- "change the JSON result schema" → use `json-contract-maintainer`
- "set up a model backend" → use `model-setup-maintainer`

## Core Files

- `mq_image_analyze/mcp/server.py`
- `mq_image_analyze/mcp/tools/__init__.py`
- `mq_image_analyze/mcp/schemas/__init__.py`
- `docs/mcp-tools.md`
- `docs/tool-safety.md`
- `docs/integration.md`
- `tests/test_mcp_tools.py`
- `tests/test_json_schema.py`

## Safety Contract

All MCP tools are read-only by default. They inspect image files and return
structured analysis. They must not write, delete, mutate, or suppress detector
output.

Keep the safety classification aligned with `docs/tool-safety.md`.

## No Silent Omission Rule

For exhaustive mode:

- preserve every detection
- include confidence, bbox, area percent, and source model
- include content flags
- include limitations
- do not hide uncertain detections without reporting why

## Tool Contract Changes

When changing an MCP tool:

1. Update implementation.
2. Update schema/docs in `docs/mcp-tools.md`.
3. Update JSON contract docs if output changes.
4. Add or update `tests/test_mcp_tools.py`.
5. Check mq-agent and mq-mcp integration docs when relevant.

## Verification

```bash
python -m pytest tests/test_mcp_tools.py tests/test_json_schema.py -q
python -m compileall mq_image_analyze/mcp -q
```

For full safety:

```bash
bash scripts/validate.sh
```
