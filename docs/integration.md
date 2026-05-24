# Integration

mq-image-analyze is the visual perception layer in the MQ ecosystem.

---

## Role

```text
mq-agent        orchestrator
mq-mcp          tool server
mq-image-analyze   perception layer
repo-signal     repo health analysis
mqlaunch        execution bridge
```

---

## mq-agent

mq-image-analyze provides visual reasoning skills for mq-agent dispatch.

Skills available:

- `visual-reasoning` — full image analysis
- `reverse-prompt` — prompt extraction from image
- `screenshot-ui-review` — UI critique (Phase 3)
- `image-quality-audit` — scoring (Phase 2)

Planned integration: skill loader reads from `skills/` and exposes them to mq-agent via standard SKILL.md contracts.

---

## mq-mcp

mq-image-analyze MCP tools (v0.4.0) will be registered in mq-mcp's tool index.

Planned tools:

```text
analyze_image()
extract_palette()
reverse_prompt()
compare_images()
score_image()
analyze_ui()
ocr_image()
```

See [mcp-tools.md](mcp-tools.md) for full contracts.

---

## repo-signal

mq-image-analyze can analyze screenshots of repo README pages, dashboards, and documentation.

Planned use: `repo-signal` can call `analyze_ui` on rendered README screenshots to evaluate visual quality of documentation.

---

## mqlaunch

mq-image-analyze CLI commands are designed to be invoked via mqlaunch.

```bash
mqlaunch run mq-image analyze screenshot.png --json
```

Output is stable JSON (see [json-schema.md](json-schema.md)) for pipeline composition.

---

## Direct CLI use

```bash
mq-image analyze image.jpg
mq-image analyze image.jpg --json | jq '.objects'
```

All `--json` output follows the v1 schema contract.
