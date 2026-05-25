---
name: cli-maintainer
description: Use when changing mq-image CLI commands, flags, output, doctor checks, serve commands, or command documentation.
---

# CLI Maintainer

Use this skill for the `mq-image` command surface.

## Core Files

- `mq_image_analyze/cli/analyze.py`
- `mq_image_analyze/cli/analyze_ui.py`
- `mq_image_analyze/cli/compare.py`
- `mq_image_analyze/cli/doctor.py`
- `mq_image_analyze/cli/serve.py`
- `mq_image_analyze/cli/serve_mcp.py`
- `mq_image_analyze/cli/__init__.py`
- `docs/cli.md`
- `README.md`
- `tests/test_cli.py`
- `tests/test_doctor.py`

## Command Surface

Known commands:

- `mq-image analyze <image>`
- `mq-image analyze <image> --json`
- `mq-image analyze <image> --mode local-fast|local-deep|cloud-verify`
- `mq-image analyze-ui <screenshot>`
- `mq-image compare <before> <after>`
- `mq-image serve --port 8000`
- `mq-image mcp`
- `mq-image doctor`
- `mq-image doctor --json`
- `mq-image --version`

## Change Rules

- Keep human output compact and useful.
- Keep `--json` machine-readable with no ANSI decoration.
- Preserve exit behavior for failed image paths and missing dependencies.
- Update `docs/cli.md` and README command examples when flags change.
- Add tests for new flags, modes, or output markers.

## Verification

```bash
python -m pytest tests/test_cli.py tests/test_doctor.py -q
mq-image --help
mq-image --version
mq-image doctor --json
```

Run the full validation script before release:

```bash
bash scripts/validate.sh
```
