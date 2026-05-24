# Architecture

## Principle

mq-image-analyze is a visual reasoning engine.
It is not primarily a generator — it is a perception layer.

## Pipeline

```text
Image input
  → Vision extraction
  → Reasoning layer
  → Structured output
  → CLI / MCP / agent workflows
```

## Three layers

### Vision

Raw signal extraction from images. Deterministic. Fast. No LLMs.

| Module | Purpose |
| ------ | ------- |
| `vision/detection` | Object detection via YOLOv8n |
| `vision/palette` | Dominant colors, brightness, contrast |
| `vision/composition` | Rule-of-thirds, symmetry, visual weight, depth |
| `vision/ocr` | Text extraction via EasyOCR |
| `vision/metadata` | EXIF, format, resolution |
| `vision/screenshot` | UI-specific signal extraction |
| `vision/segmentation` | Region and semantic segmentation |

### Reasoning

Interpretation of vision signals into human-readable and structured outputs.

| Module | Purpose |
| ------ | ------- |
| `reasoning/prompts` | Reverse prompt builder from vision signals |
| `reasoning/cinematic` | Cinematic language and lighting style analysis |
| `reasoning/styles` | Visual style classification |
| `reasoning/scoring` | Composition, realism, clarity scores |
| `reasoning/ui_analysis` | UI design pattern recognition |
| `reasoning/comparisons` | Multi-image comparison and drift detection |

### Experience

The output interfaces. Generation is optional.

| Module | Purpose |
| ------ | ------- |
| `cli/` | Typer-based CLI commands |
| `mcp/` | FastMCP server and tool definitions |
| `pipelines/` | End-to-end analysis flows |
| `adapters/` | External system integrations |

## Design constraints

- Vision layer must be **deterministic** — same image, same output.
- Reasoning layer must produce **structured, explainable** output.
- MCP tools must be **composable** — each tool does one thing.
- Generation is always **secondary** — understanding comes first.

## Model philosophy

Models are replaceable dependencies, not product features.

```text
models/      gitignored, not committed
             install with: mq-image models install yolov8n
```
