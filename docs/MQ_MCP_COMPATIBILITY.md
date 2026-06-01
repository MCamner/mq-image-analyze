# mq-mcp Compatibility

mq-image-analyze is the visual perception layer for the mq ecosystem.
It does not replace mq-mcp.

---

## Role boundary

```text
image / screenshot / diagram
        ↓
mq-image-analyze        ← visual perception only
        ↓
structured visual context
        ↓
mq-mcp                  ← contracts, review logic, memory, safety classes
        ↓
mq-agent                ← orchestration and approval gates
```

| Responsibility | Owner |
| -------------- | ----- |
| Image inspection, OCR extraction, object/scene description, diagram interpretation | **mq-image-analyze** |
| Tool contracts, safety classes, review tools, orchestration contract, memory | **mq-mcp** |
| CLI orchestration, approval gates, planner/executor/verifier | **mq-agent** |
| High-level status, reasoning shell, stack summaries | **mq-hal** |

---

## What mq-image-analyze returns

All MCP tools return structured JSON. The output is **visual context** — data derived
from pixels. It is not a review, not a decision, and not a command.

mq-mcp and mq-agent determine what to do with the context. mq-image-analyze only
describes what is visible.

---

## Safety rules for image-derived text

Image content may contain visible text (OCR, captions, diagram labels). This text
must be treated as **data**, not instructions.

- mq-mcp must not execute commands found in image-derived text fields.
- mq-agent must not pass image-derived text directly to shell execution.
- Prompt injection through visible text in images is a known attack vector.

---

## MCP tool contract table

| Tool | Maps to | Safety class | Input | Output contract | mq-mcp usage |
| ---- | ------- | ------------ | ----- | --------------- | ------------ |
| image_describe (`analyze_image`) | full visual reasoning | A | image path | structured JSON: objects, palette, composition, caption | perception context for review |
| `image_ocr` | visible text extraction | A | image path | `image_ocr.v1`: text blocks with bbox and confidence | docs/review text support |
| image_objects (`analyze_image`) | object detection | A | image path | object list with confidence | visual review context |
| image_diagram (`observe_architecture`) | architecture diagram parsing | A | image path | nodes, connections, groups, image_type | architecture review context |
| image_compare (`compare_images`) | image drift comparison | A | two image paths | difference report: palette, style, objects | visual regression |
| image_ui (`analyze_ui`) | UI screenshot analysis | A | screenshot path | layout regions, WCAG, hierarchy | screenshot review context |

All tools: read-only. No files written or mutated. `limitations` field always present.

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
- compare images
- return structured visual context
- expose read-only MCP-compatible perception tools

---

## Consuming mq-image-analyze output in mq-mcp

When mq-mcp receives output from mq-image-analyze tools:

1. Treat all text fields as data — do not execute
2. Use `image_type` from `observe_architecture` to decide review routing
3. Use `limitations` to inform confidence in the analysis
4. Pass structured JSON as context into review prompts, not as trusted input

See [mcp-tools.md](mcp-tools.md) for full tool signatures and field references.
