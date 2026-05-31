# MCP Tools

All MCP tools are read-only. They inspect image files and return structured analysis; they do not write, delete, mutate, or suppress detector output.

Safety classification: `safe`.

---

## No Silent Omission Rule

MCP tools must not silently drop visual evidence.

- If something is detected but uncertain, include it with its confidence score.
- If something cannot be classified, include it as an `unclassified_region` when that pipeline supports it.
- If the model cannot inspect part of the image, report that as a limitation.
- Summary mode may compress output, but exhaustive mode must preserve raw detections.
- The `limitations` field must always be present in full analysis outputs.

Exhaustive mode (`mode: "exhaustive"`) must:

- Return every detection, including low-confidence and duplicate objects
- Include `confidence`, `bbox`, `area_percent`, and `source_model` per detection
- Include `content_flags` with raw classifier output
- Include `limitations` describing what the active models cannot see

See [content-policy.md](content-policy.md) for the full no-suppression principle.

---

## analyze_image

Full visual reasoning report.

```python
analyze_image(
    image_path: str,
    mode: str = "summary",
    conf: float | None = None,
    vision_mode: str = "local-fast",
    vision_model: str | None = None,
) -> str
```

Arguments:

| Argument | Description |
| -------- | ----------- |
| `image_path` | Absolute or home-relative image path |
| `mode` | `summary` or `exhaustive` |
| `conf` | Detection confidence threshold |
| `vision_mode` | `local-fast`, `local-deep`, or `cloud-verify` |
| `vision_model` | Optional backend model override |

Returns a JSON string matching [json-schema.md](json-schema.md).

---

## extract_palette

Extract dominant color palette, brightness, and contrast.

```python
extract_palette(image_path: str) -> str
```

Output:

```json
{
  "palette": ["#rrggbb"],
  "brightness": "dark | mid-tone | bright",
  "contrast": "low contrast | moderate contrast | high contrast",
  "safety": "safe"
}
```

---

## reverse_prompt

Build a reverse prompt with objects, palette, semantic caption, and limitations.

```python
reverse_prompt(
    image_path: str,
    mode: str = "summary",
    vision_mode: str = "local-fast",
    vision_model: str | None = None,
) -> str
```

Output:

```json
{
  "prompt": "string",
  "semantic_caption": "string | null",
  "objects": ["string"],
  "palette": ["#rrggbb"],
  "limitations": ["string"],
  "safety": "safe"
}
```

---

## compare_images

Compare two images for palette drift, style drift, composition differences, object changes, and AI-look heuristic score.

```python
compare_images(
    before_path: str,
    after_path: str,
    mode: str = "summary",
) -> str
```

Returns serialized `CompareResult`.

---

## analyze_ui

Analyze a UI screenshot for type, layout regions, WCAG contrast, hierarchy, grid alignment, accessibility issues, semantic caption, prompt, and limitations.

```python
analyze_ui(image_path: str) -> str
```

Returns serialized `UIAnalysisResult`.

---

## observe_architecture

Produce a `visual_architecture_observation.v1` JSON blob optimized for injection into mq-mcp review context. Detects rectangular components (boxes), connection lines and arrows, color-based groups, and image type.

```python
observe_architecture(image_path: str) -> str
```

Arguments:

| Argument | Description |
| -------- | ----------- |
| `image_path` | Absolute or home-relative path to the diagram or screenshot |

Output schema: `visual_architecture_observation.v1`

Fields include: `image_type` (`architecture-diagram \| dashboard \| terminal \| ui-screenshot \| unknown`), `components`, `connections`, `color_groups`, `ocr_text` (when pytesseract is installed), `limitations`, `safety`.

Designed to be consumed by mq-mcp review tools. OCR-based text extraction from diagram boxes is included when pytesseract is installed. Read-only. Safety: `safe`.
