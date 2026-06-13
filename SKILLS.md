# Skills

mq-image-analyze provides visual reasoning skills for AI agents and automated workflows.

The table below is generated from SKILL.md frontmatter by
`./scripts/check-skills.sh --fix`. Do not edit it by hand. Per-skill phase and
status metadata lives in each SKILL.md's frontmatter.

<!-- BEGIN GENERATED SKILLS TABLE -->
| Skill | Description |
| ----- | ----------- |
| [cli-maintainer](skills/cli-maintainer/SKILL.md) | Use when changing mq-image CLI commands, flags, output, doctor checks, serve commands, or command documentation. |
| [docs-maintainer](skills/docs-maintainer/SKILL.md) | Use when keeping mq-image-analyze README, docs, examples, CLI docs, MCP docs, schema docs, release docs, or integration docs consistent with code. |
| [image-quality-audit](skills/image-quality-audit/SKILL.md) | Use when scoring an image for composition quality, clarity, and visual hierarchy. |
| [json-contract-maintainer](skills/json-contract-maintainer/SKILL.md) | Use when changing mq-image-analyze JSON output schemas, analysis result fields, compare output, UI analysis output, exhaustive mode, or stable integration contracts. |
| [mcp-tools-maintainer](skills/mcp-tools-maintainer/SKILL.md) | Use when changing mq-image-analyze MCP server, MCP tool schemas, tool safety, read-only behavior, or mq-mcp/mq-agent integration. |
| [model-setup-maintainer](skills/model-setup-maintainer/SKILL.md) | Use when changing mq-image-analyze model setup, YOLO weights, Ollama/OpenAI vision backends, doctor readiness checks, or model documentation. |
| [release-readiness](skills/release-readiness/SKILL.md) | Use when preparing mq-image-analyze for release by checking version sync, docs, tests, CLI, MCP tools, model safety, examples, and Git state. |
| [repo-aware](skills/repo-aware/SKILL.md) | Use when inspecting, explaining, planning, reviewing, or changing mq-image-analyze with repository-specific context. |
| [reverse-prompt](skills/reverse-prompt/SKILL.md) | Use when turning an image into a reusable prompt for image generation, visual design, or cinematic direction. |
| [screenshot-ui-review](skills/screenshot-ui-review/SKILL.md) | Use when reviewing screenshots of apps, terminals, dashboards, websites, or GitHub pages for layout and usability. |
| [visual-architecture-analysis](skills/visual-architecture-analysis/SKILL.md) | Use when adding or changing mq-image-analyze features for architecture diagrams, infrastructure topology screenshots, terminal screenshots, OCR pipelines, or visual observations consumed by mq-mcp. |
| [visual-reasoning](skills/visual-reasoning/SKILL.md) | Use when analyzing an image for objects, palette, composition, mood, visual hierarchy, and prompt intent. |
| [web-ui-maintainer](skills/web-ui-maintainer/SKILL.md) | Use when changing mq-image-analyze web UI, FastAPI web server, packaged web assets, serve command, local ports, upload flow, or browser review workflow. |
<!-- END GENERATED SKILLS TABLE -->

## Integration

These skills are designed to be consumed by:

- `mq-agent` (skill dispatch)
- `mq-mcp` (MCP tool wrapping)
- Claude Code / Codex (direct invocation)

Each skill has a `SKILL.md` that defines inputs, outputs and constraints.
