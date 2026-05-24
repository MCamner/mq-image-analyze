# Skills

mq-image-analyze provides visual reasoning skills for AI agents and automated workflows.

| Skill | Description | Status |
| ----- | ----------- | ------ |
| [visual-reasoning](skills/visual-reasoning/SKILL.md) | Analyze image content, palette, composition, and prompt intent | Phase 1 |
| [reverse-prompt](skills/reverse-prompt/SKILL.md) | Convert an image into a reusable generation prompt | Phase 1 |
| [screenshot-ui-review](skills/screenshot-ui-review/SKILL.md) | Review UI screenshots for layout, contrast, and usability | Phase 3 |
| [image-quality-audit](skills/image-quality-audit/SKILL.md) | Score composition, clarity, and visual hierarchy | Phase 2 |

## Integration

These skills are designed to be consumed by:

- `mq-agent` (skill dispatch)
- `mq-mcp` (MCP tool wrapping)
- Claude Code / Codex (direct invocation)

Each skill has a `SKILL.md` that defines inputs, outputs, and constraints.
