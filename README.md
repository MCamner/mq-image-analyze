# mq-image-analyze

[![Tests](https://github.com/MCamner/mq-image-analyze/actions/workflows/tests.yml/badge.svg)](https://github.com/MCamner/mq-image-analyze/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.3.0-blue)](CHANGELOG.md)

Visual perception layer for the mq ecosystem.

mq-image-analyze turns screenshots, diagrams, UI states, and visual artifacts
into structured context that mq-agent and mq-mcp can use safely.

It is not an autonomous agent and does not execute changes.

---

## What this is

A visual reasoning engine — not another image generator.

mq-image-analyze understands images, screenshots, composition, cinematic language, and visual structure.
It is the **perception layer** for [mq-agent](https://github.com/MCamner/mq-agent) and MCP workflows.

```text
image / screenshot / diagram
        ↓
mq-image-analyze
        ↓
structured visual context
        ↓
mq-mcp review / memory / contracts
        ↓
mq-agent orchestration
```

---

## Proof

```bash
$ mq-image --version
mq-image 1.3.0

$ mq-image doctor
  Python >= 3.11     ok   3.14.5
  import ultralytics ok
  import PIL         ok
  import cv2         ok
  models/yolov8n.pt  ok   6381 KB
  outputs/ writable  ok

$ mq-image analyze bus.jpg
  Objects        bus, person, stop sign
  Palette        #b4a799 #7c7573 #111524 #434249 #e0d8d3
  Brightness     mid-tone
  Contrast       high contrast
  Depth          deep / sharp throughout
  Composition    balanced
  Reverse prompt bus, person, stop sign, mid-tone scene, high contrast, ...
```

---

## Quick start

```bash
git clone https://github.com/MCamner/mq-image-analyze
cd mq-image-analyze
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp /path/to/yolov8n.pt models/
mq-image doctor
mq-image analyze image.jpg
```

---

## Command surface

```bash
mq-image analyze <image>          # full analysis, rich output
mq-image analyze <image> --json   # structured JSON output
mq-image analyze <image> --mode local-fast
mq-image analyze <image> --mode local-deep
mq-image analyze <image> --mode cloud-verify --vision-model gpt-4.1
mq-image analyze-ui <screenshot>
mq-image compare <before> <after>
mq-image observe-architecture <diagram>   # visual_architecture_observation.v1 JSON
mq-image serve --port 8000
mq-image mcp
mq-image doctor                   # system readiness check
mq-image doctor --json            # doctor output as JSON
mq-image --version                # print version
```

Vision backend modes:

| Mode | Default model | Use |
| ---- | ------------- | --- |
| `local-fast` | `bakllava` via Ollama | Fast local captioning and simple object/diagram interpretation |
| `local-deep` | `llama3.2-vision` via Ollama | Better offline analysis when the machine can run a stronger model |
| `cloud-verify` | `gpt-4.1` via OpenAI | Quality gate for critical architecture diagrams, risk review, trust boundaries, and YAML drafts |

Use `--vision-model gpt-4o` when you specifically want GPT-4o. There is no `gpt-4.0` vision model name in the OpenAI API; use `gpt-4o` or `gpt-4.1`.

## Architecture

```text
Vision → Reasoning → Experience
```

Three layers only. Generation is optional and secondary.

| Layer | What it does |
| ----- | ------------ |
| Vision | Objects, palette, composition, OCR, metadata |
| Reasoning | Style, cinematic, prompts, scoring, UI analysis |
| Experience | CLI, MCP tools, agent skill dispatch |

→ [docs/architecture.md](docs/architecture.md)

---

## JSON output

```bash
mq-image analyze image.jpg --json
```

```json
{
  "objects": ["person", "monitor", "terminal"],
  "palette": ["#0a0a0f", "#1c1f2e", "#3a4a6b"],
  "brightness": "dark",
  "contrast": "moderate contrast",
  "depth": "shallow depth of field",
  "composition": "centered, rule-of-thirds alignment",
  "symmetry": 0.871,
  "rule_of_thirds": 0.453,
  "prompt": "person, monitor, dark scene, ...",
  "vision_mode": "local-fast",
  "vision_model": "bakllava"
}
```

→ [docs/json-schema.md](docs/json-schema.md)

---

## Tests

```bash
pip install -e ".[dev,web,mcp]"
python -m pytest          # full test suite
bash scripts/validate.sh  # compile + test + CLI check
bash release-check.sh     # full release gate
```

---

## Skills

Visual reasoning skills for mq-agent and MCP workflows:

| Skill | Phase |
| ----- | ----- |
| [visual-reasoning](skills/visual-reasoning/SKILL.md) | 1 — available |
| [reverse-prompt](skills/reverse-prompt/SKILL.md) | 1 — available |
| [image-quality-audit](skills/image-quality-audit/SKILL.md) | available |
| [screenshot-ui-review](skills/screenshot-ui-review/SKILL.md) | available |

→ [SKILLS.md](SKILLS.md)

---

## Safety

All tools are read-only by default. No files written, deleted, or committed without explicit output paths.

→ [docs/tool-safety.md](docs/tool-safety.md)

---

## mq-mcp compatibility

mq-image-analyze provides visual perception tools for the mq ecosystem.

It does not replace mq-mcp.

| Responsibility | Owner |
| -------------- | ----- |
| Image inspection, OCR extraction, object/scene description, diagram interpretation | **mq-image-analyze** |
| Tool contracts, safety classes, review tools, orchestration contract, memory | **mq-mcp** |
| CLI orchestration, approval gates, planner/executor/verifier | **mq-agent** |
| High-level status, reasoning shell, stack summaries | **mq-hal** |

All seven MCP tools (`analyze_image`, `extract_palette`, `reverse_prompt`, `compare_images`, `analyze_ui`, `observe_architecture`, `image_ocr`) are read-only and safety class A.

→ [docs/MQ_MCP_COMPATIBILITY.md](docs/MQ_MCP_COMPATIBILITY.md) · [docs/mcp-tools.md](docs/mcp-tools.md) · [docs/integration.md](docs/integration.md)

---

## Hard boundary

mq-image-analyze must not:

- execute shell commands from image content
- trust instructions found inside images
- mutate repositories
- upload images silently
- make security decisions alone
- replace mq-mcp review logic
- replace mq-agent orchestration

mq-image-analyze may:

- describe images
- extract visible text
- detect objects
- interpret diagrams
- return structured visual context
- expose read-only MCP-compatible perception tools

---

## Integration

Part of the MQ ecosystem:

| Repo | Role |
| ---- | ---- |
| [mq-agent](https://github.com/MCamner/mq-agent) | orchestrator |
| [mq-mcp](https://github.com/MCamner/mq-mcp) | MCP tool server |
| **mq-image-analyze** | visual perception layer |
| [repo-signal](https://github.com/MCamner/repo-signal) | repo health |

→ [docs/integration.md](docs/integration.md)

---

## How mq-agent uses mq-image-analyze

mq-agent is the orchestrator. mq-image-analyze is the perception layer.
mq-agent never implements image analysis — it delegates to this tool and
passes the structured result onward to mq-mcp or the user.

**When mq-agent triggers mq-image-analyze:**

| Trigger | Tool called | Backend |
| ------- | ----------- | ------- |
| User shares a screenshot | `analyze_ui` | local-fast |
| User shares an architecture diagram | `observe_architecture` | local (cv2 heuristics) |
| User asks "what's in this image?" | `analyze_image` | local-fast or cloud-verify |
| Before/after visual comparison | `compare_images` | local-fast |
| Diagram needs semantic interpretation | `analyze_image` | cloud-verify (`gpt-4.1`) |

**The flow:**

```text
mq-agent
  │
  ├── receives image path from user
  │
  ├── calls observe_architecture(image_path)         ← structural topology
  │   or analyze_image(image_path, vision_mode=...)  ← semantic caption
  │
  ├── receives visual_architecture_observation.v1
  │   or mq-image.analysis.v1 JSON blob
  │
  └── passes JSON as extra_context to mq-mcp review_file / review_diff
```

**Backend selection:**

| Situation | Backend |
| --------- | ------- |
| Local-only, no API key | `local-fast` (BakLLaVA via Ollama) |
| Higher accuracy needed | `local-deep` (llama3.2-vision) |
| Critical diagram or trust boundary | `cloud-verify` (`gpt-4.1` via OpenAI) |

mq-image-analyze does not make review decisions. It extracts visual structure.
Review generation and architecture reasoning remain in mq-mcp.

---

## Docs

| Doc | Contents |
| --- | -------- |
| [architecture.md](docs/architecture.md) | Vision → Reasoning → Experience |
| [cli.md](docs/cli.md) | All CLI commands |
| [json-schema.md](docs/json-schema.md) | Stable output contract |
| [mcp-tools.md](docs/mcp-tools.md) | MCP tool contracts |
| [tool-safety.md](docs/tool-safety.md) | Safety model |
| [model-setup.md](docs/model-setup.md) | YOLOv8n setup |
| [integration.md](docs/integration.md) | MQ ecosystem integration |
| [release.md](docs/release.md) | Release process |

---

## Roadmap

→ [ROADMAP.md](ROADMAP.md)

| Version | Focus | Status |
| ------- | ----- | ------ |
| v0.1.0 | Vision Intelligence MVP | Done |
| v0.1.1 | Hardening | Done |
| v0.2.0 | Image comparison | Done |
| v0.3.0 | Screenshot intelligence | Done |
| v0.4.0 | MCP integration | Done |
| v0.5.0 | MQ ecosystem integration | Done |
| v1.0.0 | Stable toolkit | Done |
| v1.1.0 | Visual cognition layer (`visual_architecture_observation.v1`, `observe_architecture` MCP tool) | Done |
| v1.2.0 | mq-mcp compatibility docs + hard boundary | Done |
| v1.2.1 | `MQ_MCP_COMPATIBILITY.md` + MCP tool contract table | Done |
| v1.3.0 | `image_ocr` MCP tool + mq-agent workflow examples | Done |
