# CLI Reference

Entry point: `mq-image`

Global options:

```bash
mq-image --version
mq-image --help
mq-image <command> --help
```

---

## analyze

Analyze an image: objects, palette, composition, content flags, semantic caption, and reverse prompt.

```bash
mq-image analyze <image>
mq-image analyze <image> --json
mq-image analyze <image> --exhaustive --conf 0.05
mq-image analyze <image> --mode local-fast
mq-image analyze <image> --mode local-deep
mq-image analyze <image> --mode cloud-verify --vision-model gpt-4.1
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image` | path | yes | Path to image file |
| `--json` | flag | no | Output raw JSON instead of rich terminal output |
| `--exhaustive` | flag | no | Preserve every raw detection, including duplicates |
| `--conf` | float | no | Detection confidence threshold |
| `--mode` | string | no | Vision backend: `local-fast`, `local-deep`, or `cloud-verify` |
| `--vision-model` | string | no | Override backend model, for example `gpt-4o` or `gpt-4.1` |

Backend defaults:

| Mode | Default model | Notes |
| ---- | ------------- | ----- |
| `local-fast` | `bakllava` | Default Ollama path |
| `local-deep` | `llama3.2-vision` | Stronger local Ollama path when available |
| `cloud-verify` | `gpt-4.1` | OpenAI quality gate; requires `OPENAI_API_KEY` |

For GPT-4o:

```bash
mq-image analyze diagram.png --mode cloud-verify --vision-model gpt-4o
```

---

## analyze-ui

Analyze a UI screenshot: screenshot type, layout regions, WCAG contrast ratio, hierarchy, grid alignment, accessibility issues, and prompt.

```bash
mq-image analyze-ui <screenshot>
mq-image analyze-ui <screenshot> --json
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image` | path | yes | Path to screenshot |
| `--json` | flag | no | Output raw JSON |

---

## compare

Compare two images for visual drift.

```bash
mq-image compare <before> <after>
mq-image compare <before> <after> --json
mq-image compare <before> <after> --exhaustive --conf 0.05
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `before` | path | yes | Baseline image |
| `after` | path | yes | Changed image |
| `--json` | flag | no | Output raw JSON |
| `--exhaustive` | flag | no | Use exhaustive detection mode |
| `--conf` | float | no | Detection confidence threshold |

---

## doctor

Check system readiness: Python version, required packages, model files, and output permissions.

```bash
mq-image doctor
mq-image doctor --json
```

---

## serve

Start the local web UI.

```bash
mq-image serve
mq-image serve --host 127.0.0.1 --port 8000
mq-image serve --reload
```

Install web dependencies with:

```bash
pip install -e ".[web]"
```

---

## mcp

Start the MCP server.

```bash
mq-image mcp
mq-image mcp --transport stdio
mq-image mcp --transport sse
```

Install MCP dependencies with:

```bash
pip install -e ".[mcp]"
```
