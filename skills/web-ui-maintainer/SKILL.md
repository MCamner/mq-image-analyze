---
name: web-ui-maintainer
description: Use when changing mq-image-analyze web UI, FastAPI web server, packaged web assets, serve command, local ports, upload flow, or browser review workflow.
---

# Web UI Maintainer

Use this skill for `mq-image serve` and browser-based image analysis.

## Evals

### Should trigger

- "fix the web upload flow"
- "the serve command port handling is wrong"
- "improve the browser review workflow"
- "the packaged web assets are stale"

### Should not trigger

- "change the CLI" → use `cli-maintainer`
- "change MCP tools" → use `mcp-tools-maintainer`
- "update web docs only" → use `docs-maintainer`

## Core Files

- `mq_image_analyze/cli/serve.py`
- `mq_image_analyze/web/server.py`
- `mq_image_analyze/web/index.html`
- `web/server.py`
- `web/index.html`
- `tests/test_web_package.py`
- `docs/cli.md`
- `README.md`

## UI Contract

- The web UI should expose image upload/analysis clearly.
- The packaged web assets under `mq_image_analyze/web/` must stay in sync with
  root `web/` assets when both are used.
- `mq-image serve --port 8000` should be documented and testable.
- Browser output should reflect the same JSON contracts as CLI/MCP where
  applicable.

## Change Rules

- Keep local server bind/port behavior explicit.
- Do not add analytics or external uploads without explicit user request.
- Keep file upload handling scoped and temporary.
- Update package data if new static assets are introduced.
- Add tests when packaging or route behavior changes.

## Verification

```bash
python -m pytest tests/test_web_package.py -q
mq-image serve --help
```

Manual check:

```bash
mq-image serve --port 8000
```

Then open `http://127.0.0.1:8000`.
