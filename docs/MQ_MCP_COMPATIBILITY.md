# mq-mcp Compatibility

mq-image-analyze is the visual perception layer for the mq ecosystem.
It does not replace mq-mcp.

---

## Normalized perception record — `perception.v1`

Each pipeline here reports what it found in its own words: `screenshot_type` or
`image_type`, `full_text` or `text_regions`, `semantic_caption` or `prompt`,
`issues` or nothing at all. That is workable inside a pipeline and useless
across a repository boundary. `mq_image_analyze.perception` normalizes any of
them into one record.

```json
{
  "schema_version": "perception.v1",
  "source_type": "screenshot | diagram | ui | terminal | browser",
  "source_path": "diagram.png",
  "ocr_text": "",
  "visual_summary": "1 component(s), 0 connection(s), 1 group(s)",
  "detected_regions": [],
  "risk_signals": [],
  "confidence": "low | medium | high",
  "limitations": []
}
```

Samples: `examples/perception/` (one per producer). Cross-repo fixture:
`tests/fixtures/sample_perception_output.json`.

### Who owns which half

**mq-mcp owns the required fields.** `release_gate/checks.py` validates
perception artifacts and blocks a release on an invalid one, so `source_type`,
`source_path`, `ocr_text`, `visual_summary`, `risk_signals`, `confidence` and
the two vocabularies were frozen there. This repo satisfies that contract; it
does not define it, and cannot extend either vocabulary from this side.

**This repo owns what it adds.** `schema_version` and `limitations` are the
conventions here since v1.4. They are additive: the consumer checks the keys it
requires and does not reject the ones it does not, which is pinned by a test.

### Compatibility rules

* No perception happens during normalization. Every field is a rename, a join,
  or a restatement of counts the producer already established.
* A producer that does not know something does not guess it. An OCR run knows
  neither the kind of image nor its path, so the caller supplies both.
* A producer vocabulary with no honest equivalent raises rather than picking the
  closest one. `unknown` is not a kind of image, and a `dashboard` is as
  defensibly a `ui` as a `screenshot` — both defer to the caller.
* A producer value that *does* map wins over a caller hint. The producer
  observed it; a hint does not get to contradict it.

### `confidence` means something different here than elsewhere in this repo

The word is already taken. A region carries a float: how sure the detector is
about one box. The record-level `confidence` answers a different question —
**how complete this record is** — and is derived, never asserted:

| | |
| --- | --- |
| `low` | nothing was extracted: no text, no regions, no summary |
| `medium` | something was extracted, but a capability the producer has was unavailable, or only one field carries content |
| `high` | the capabilities were available and at least two of the three content fields carry something |

It is never a claim about accuracy. Per-region floats keep their own meaning
inside `detected_regions`.

---

## How perception output is consumed

What exists today:

```text
mq-image-analyze
      ↓  perception.v1 artifact
mq-mcp release gate            check_perception_artifacts_valid
      ↓                        blocks the release on an invalid artifact
mq-mcp perception review tools image_observe_architecture, image_analyze_ui,
                               image_analyze — read-only, pass output as
                               context to review_repo / review_file
```

The gate finds artifacts by path. `tests/fixtures/*perception*.json`,
`perception/**/*.json`, `reports/perception*.json` and `docs/perception*.json`
are picked up automatically, which is why the shipped fixture lives where it
does.

One caveat worth stating plainly: with no artifact in a repo the check reports
`No perception artifacts found; nothing to validate` and passes. That is
indistinguishable from a real validation unless something is actually there.

`mq-agent review perception <image>` does **not** exist. `mq-agent review`
offers `file`, `diff` and `repo`, and mq-agent carries no perception command;
it delegates image work to this repo rather than analyzing locally. The chain
above is the one that works today, and that command is a separate piece of
work in mq-agent, not part of this contract.

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
