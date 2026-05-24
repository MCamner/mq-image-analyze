# mq-image-analyze

Visual reasoning and image intelligence for AI agents,
creative workflows, screenshots, and cinematic analysis.

> "People don't want image tooling. They want understanding."

---

## What this is

A visual reasoning engine. Not another image generator.

mq-image-analyze understands:

- images, screenshots, design
- composition, cinematic language, visual structure
- UI layouts, prompt intent, aesthetic logic

It is the **perception layer** for mq-agent and MCP workflows.

---

## Architecture

```text
Vision → Reasoning → Experience
```

Three layers only. Generation is optional and secondary.
→ [docs/architecture.md](docs/architecture.md)

---

## Phase 1 — Vision Intelligence MVP

```bash
mq-image analyze image.jpg
mq-image analyze image.jpg --json
```

Output:

```text
Objects:        person, monitor, terminal
Palette:        #0a0a0f #1c1f2e #3a4a6b #c8d4e8 #f0f4ff
Brightness:     dark
Contrast:       moderate contrast
Depth:          shallow depth of field
Composition:    left-heavy, rule-of-thirds alignment
Reverse prompt: person, monitor, dark scene, moderate contrast, ...
```

→ [examples/sample-cli-output.txt](examples/sample-cli-output.txt)
→ [examples/sample-analysis.json](examples/sample-analysis.json)

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Models are not committed. Place `yolov8n.pt` in `models/`.

---

## Tests

```bash
pip install -e ".[dev]"
pytest
```

---

## Roadmap

| Phase | Focus |
| ----- | ----- |
| 1 | analyze, reverse-prompt, palette, composition |
| 2 | compare, score, style-drift, AI-look detection |
| 3 | screenshot intelligence, UI analysis, layout |
| 4 | generation (optional, never dominant) |

→ [ROADMAP.md](ROADMAP.md)

---

## Structure

```text
mq_image_analyze/
  vision/        object detection, palette, composition, OCR
  reasoning/     styles, cinematic, prompts, scoring, UI
  mcp/           MCP server and tool definitions
  cli/           CLI commands
  adapters/      external system integrations
  pipelines/     end-to-end analysis flows
models/          local weights (gitignored)
docs/            architecture and decisions
```

---

## MCP Tools

```text
analyze_image()     reverse_prompt()    extract_palette()
extract_style()     compare_images()    score_image()
analyze_ui()        ocr_image()
```

All tools are deterministic, explainable, structured, composable.
→ [docs/mcp-tools.md](docs/mcp-tools.md)
