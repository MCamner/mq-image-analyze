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

mq-image-analyze provides visual reasoning skills for mq-agent dispatch via the `skills/` directory and SKILL.md contracts.

Skills available:

- `visual-reasoning` — full image analysis via `analyze_image`
- `reverse-prompt` — prompt extraction from image via `reverse_prompt`
- `screenshot-ui-review` — UI critique via `analyze_ui`
- `architecture-observation` — diagram parsing via `observe_architecture`

---

## mq-mcp

mq-image-analyze exposes a native MCP server (`mq-image mcp`) that mq-mcp can route tool calls to as a visual perception backend.

Active tools (v1.1.0+, compatible with mq-mcp v1.3.0+):

```text
analyze_image()          — full visual reasoning report
extract_palette()        — dominant color palette
reverse_prompt()         — reverse prompt from image
compare_images()         — image drift comparison
analyze_ui()             — UI screenshot critique
observe_architecture()   — visual_architecture_observation.v1 for mq-mcp review context
```

All tools are read-only. Safety classification: `safe`.

See [mcp-tools.md](mcp-tools.md) for full contracts and argument signatures.

---

## repo-signal

mq-image-analyze can analyze screenshots of repo README pages, dashboards, and documentation. `repo-signal` can call `analyze_ui` on rendered README screenshots to evaluate visual quality of documentation.

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
