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
| `vision/ui` | Screenshot type, layout regions, WCAG contrast, hierarchy |
| `vision/architecture` | Diagram components, connections, color groups, image type |
| `vision/content` | Content flags (NudeNet) |
| `vision/semantic` | Optional captions via Ollama or OpenAI vision |

### Reasoning

Interpretation of vision signals into human-readable and structured outputs.

| Module | Purpose |
| ------ | ------- |
| `reasoning/prompts` | Reverse prompt builder from vision signals |
| `reasoning/comparison` | Two-image comparison and drift detection |

### Experience

The output interfaces. Generation is optional.

| Module | Purpose |
| ------ | ------- |
| `cli/` | Typer-based CLI commands |
| `mcp/` | FastMCP server and tool definitions |
| `web/` | FastAPI upload UI (`mq-image serve`) |
| `pipelines/` | OCR (pytesseract, optional) and architecture observation flows |
| `perception.py` | Normalized `perception.v1` record for mq-mcp Release Gate v2 |

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
