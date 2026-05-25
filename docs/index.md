---
layout: default
title: mq-image-analyze
---

# mq-image-analyze

Visual reasoning infrastructure for image analysis.

**v0.5.0** — Object detection · Palette extraction · Composition analysis · Content flags · Semantic captions · UI analysis · Image comparison · MCP tools

---

## Quick start

```bash
pip install -e ".[web,mcp]"
mq-image analyze image.png
mq-image analyze-ui screenshot.png
mq-image compare before.png after.png
mq-image serve --port 9999
mq-image mcp
```

---

## Commands

| Command | Description |
|---|---|
| `analyze` | Full image analysis — objects, palette, composition, content flags, reverse prompt |
| `analyze-ui` | UI screenshot analysis — layout, WCAG contrast, hierarchy, accessibility |
| `compare` | Compare two images — palette drift, style drift, AI-look score |
| `serve` | Web UI on localhost |
| `mcp` | Start MCP server for agent tool use |
| `doctor` | Check model and dependency health |

---

## MCP tools

| Tool | Description |
|---|---|
| `analyze_image` | Full visual reasoning |
| `extract_palette` | Colors, brightness, contrast |
| `reverse_prompt` | Prompt for image generators |
| `compare_images` | Visual drift detection |
| `analyze_ui` | Screenshot accessibility review |

All tools are read-only (safety: safe).

---

## Docs

- [Architecture](architecture.md)
- [CLI reference](cli.md)
- [MCP tools](mcp-tools.md)
- [JSON schema](json-schema.md)
- [Content policy](content-policy.md)
- [Tool safety](tool-safety.md)
- [Model setup](model-setup.md)
- [Integration](integration.md)

---

## Design principles

- **No Silent Omission** — all detector output is preserved, no suppression
- **Neutral Explicit Content** — content_flags reported as-is, never filtered
- **Limitations always present** — every response includes what the models cannot see
- **Orchestration + Intelligence** — models are replaceable dependencies, not stored artifacts
