---
name: release-readiness
description: Use when preparing mq-image-analyze for release by checking version sync, docs, tests, CLI, MCP tools, model safety, examples, and Git state.
---

# Release Readiness

Use this skill before tagging or publishing mq-image-analyze.

## Always Inspect

- `git status --short`
- `VERSION`
- `pyproject.toml`
- `CHANGELOG.md`
- `README.md`
- `SKILLS.md`
- `docs/release.md`
- `docs/json-schema.md`
- `docs/mcp-tools.md`
- `docs/tool-safety.md`
- `scripts/validate.sh`
- `release-check.sh`

## Blockers

- dirty worktree with unrelated changes
- version mismatch between `VERSION`, `pyproject.toml`, README, and changelog
- failing tests
- CLI entry point failure
- tracked model weights or `.env`
- docs missing new CLI/MCP/JSON behavior
- skill status drift
- output contract changes without schema/tests

## Verification

```bash
bash scripts/validate.sh
bash release-check.sh
```

If a narrower check is enough:

```bash
python -m compileall mq_image_analyze -q
python -m pytest -q
mq-image --help
mq-image --version
```

## Report Format

Return:

- status: ready, blocked, or uncertain
- blockers
- changed files
- checks run
- checks skipped and why
- model/API credentials not verified, if applicable
