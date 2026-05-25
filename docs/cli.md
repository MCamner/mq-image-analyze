# CLI Reference

Entry point: `mq-image`

---

## analyze

Analyze an image — objects, palette, composition, reverse prompt.

```bash
mq-image analyze <image>
mq-image analyze <image> --json
mq-image analyze <image> --mode local-fast
mq-image analyze <image> --mode local-deep
mq-image analyze <image> --mode cloud-verify --vision-model gpt-4.1
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image` | path | yes | Path to image file (jpg, png, webp) |
| `--json` | flag | no | Output raw JSON instead of rich terminal output |
| `--mode` | string | no | Vision backend: `local-fast`, `local-deep`, or `cloud-verify` |
| `--vision-model` | string | no | Override the backend model, for example `gpt-4o` or `gpt-4.1` |

Output fields: `objects`, `palette`, `brightness`, `contrast`, `depth`, `composition`, `symmetry`, `rule_of_thirds`, `prompt`, `vision_mode`, `vision_model`

Backend defaults:

| Mode | Default model | Notes |
| ---- | ------------- | ----- |
| `local-fast` | `bakllava` | Default Ollama path |
| `local-deep` | `llama3.2-vision` | Stronger local Ollama path when available |
| `cloud-verify` | `gpt-4.1` | OpenAI quality gate; requires `OPENAI_API_KEY` |

For GPT-4o, run `mq-image analyze diagram.png --mode cloud-verify --vision-model gpt-4o`.

---

## doctor

Check system readiness — dependencies, model files, permissions.

```bash
mq-image doctor
mq-image doctor --json
```

Checks:
- Python version
- Required packages installed (ultralytics, pillow, opencv-python, typer, rich)
- `models/yolov8n.pt` present
- Output directory writable
- CLI entry point functional

---

## Planned commands (v0.2+)

```bash
mq-image compare <before> <after>
mq-image score <image>
mq-image palette <image>
mq-image reverse-prompt <image>
mq-image analyze-ui <screenshot>
```

---

## Global options

```bash
mq-image --version
mq-image --help
mq-image <command> --help
```
