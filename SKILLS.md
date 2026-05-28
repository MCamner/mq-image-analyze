# Skills

mq-image-analyze provides visual reasoning skills for AI agents and automated workflows.

| Skill | Description | Status |
| ----- | ----------- | ------ |
| [cli-maintainer](skills/cli-maintainer/SKILL.md) | Maintain CLI commands and user-facing command behavior | Maintainer |
| [docs-maintainer](skills/docs-maintainer/SKILL.md) | Keep docs, examples and integration notes aligned | Maintainer |
| [image-quality-audit](skills/image-quality-audit/SKILL.md) | Score composition, clarity and visual hierarchy | Phase 2 |
| [json-contract-maintainer](skills/json-contract-maintainer/SKILL.md) | Maintain JSON schemas and stable machine-readable outputs | Maintainer |
| [mcp-tools-maintainer](skills/mcp-tools-maintainer/SKILL.md) | Maintain MCP tools and safety contracts | Maintainer |
| [model-setup-maintainer](skills/model-setup-maintainer/SKILL.md) | Maintain model setup and backend behavior | Maintainer |
| [release-readiness](skills/release-readiness/SKILL.md) | Prepare and verify releases | Maintainer |
| [repo-aware](skills/repo-aware/SKILL.md) | Work repo-first with local structure and conventions | Maintainer |
| [reverse-prompt](skills/reverse-prompt/SKILL.md) | Convert an image into a reusable generation prompt | Phase 1 |
| [screenshot-ui-review](skills/screenshot-ui-review/SKILL.md) | Review UI screenshots for layout, contrast and usability | Phase 3 |
| [visual-architecture-analysis](skills/visual-architecture-analysis/SKILL.md) | Extract architecture, topology, OCR and screenshot observations for mq-mcp | Phase 6 |
| [visual-reasoning](skills/visual-reasoning/SKILL.md) | Analyze image content, palette, composition and prompt intent | Phase 1 |
| [web-ui-maintainer](skills/web-ui-maintainer/SKILL.md) | Maintain web UI and visual presentation surfaces | Maintainer |

## Integration

These skills are designed to be consumed by:

- `mq-agent` (skill dispatch)
- `mq-mcp` (MCP tool wrapping)
- Claude Code / Codex (direct invocation)

Each skill has a `SKILL.md` that defines inputs, outputs and constraints.
