---
name: docs-maintainer
description: Use when keeping mq-image-analyze README, docs, examples, CLI docs, MCP docs, schema docs, release docs, or integration docs consistent with code.
---

# Docs Maintainer

Keep documentation synchronized with code and tests.

## Docs Surfaces

- `README.md`
- `SKILLS.md`
- `docs/architecture.md`
- `docs/cli.md`
- `docs/json-schema.md`
- `docs/mcp-tools.md`
- `docs/tool-safety.md`
- `docs/model-setup.md`
- `docs/integration.md`
- `docs/release.md`
- `docs/content-policy.md`
- `CHANGELOG.md`
- `ROADMAP.md`

## Common Drift

- Skill status mismatch between `SKILLS.md`, README, and skill frontmatter.
- CLI docs missing a new flag or mode.
- JSON docs missing a new field.
- MCP tool docs missing a tool argument or safety note.
- Model setup docs naming an invalid OpenAI/Ollama model.
- README examples not matching actual command output.

## Verification

```bash
rg "visual-reasoning|reverse-prompt|screenshot-ui-review" \
  README.md SKILLS.md skills
rg "image-quality-audit" README.md SKILLS.md skills
python -m pytest tests/test_version_consistency.py -q
```

For broader docs-related changes:

```bash
bash scripts/validate.sh
```

## Editing Guidance

Document only behavior that exists or is intentionally added in the same change.
Treat output contracts and safety docs as part of the public API.
