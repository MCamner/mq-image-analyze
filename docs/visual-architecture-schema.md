# Visual Architecture Observation Schema

Schema version: `visual_architecture_observation.v1`

Produced by `mq-image observe-architecture <image>` and the `observe_architecture` MCP tool.

Designed for consumption by mq-mcp review tools — the output can be passed directly
as context into `review_file`, `review_diff`, or `review_repo` calls.

---

## Shape

```json
{
  "schema_version": "visual_architecture_observation.v1",
  "image_type": "architecture-diagram | dashboard | terminal | ui-screenshot | unknown",
  "image_path": "string",
  "components": [
    {
      "id": "box_0",
      "bbox": [0.0, 0.0, 0.0, 0.0],
      "area_percent": 0.0,
      "label": "string or null",
      "fill_color": "#rrggbb or null",
      "text": "string or null"
    }
  ],
  "connections": [
    {
      "id": "edge_0",
      "direction": "horizontal | vertical | diagonal | unknown",
      "from_component": "box_0 or null",
      "to_component": "box_1 or null"
    }
  ],
  "groups": [
    {
      "color": "#rrggbb",
      "component_ids": ["box_0"],
      "label": "string or null"
    }
  ],
  "text_regions": [
    {
      "text": "string",
      "bbox": [0.0, 0.0, 0.0, 0.0],
      "confidence": 0.0
    }
  ],
  "layout": {
    "width": 0,
    "height": 0,
    "component_count": 0,
    "connection_count": 0,
    "dominant_flow": "left-to-right | top-to-bottom | radial | unknown"
  },
  "limitations": ["string"],
  "ocr_available": false
}
```

---

## Field reference

### Top-level

| Field | Type | Notes |
| ----- | ---- | ----- |
| `schema_version` | string | Always `visual_architecture_observation.v1` |
| `image_type` | string | Classifier result — see image types below |
| `image_path` | string | Absolute resolved path of the analyzed image |
| `components` | object[] | Detected rectangular components (boxes) |
| `connections` | object[] | Detected lines/arrows between components |
| `groups` | object[] | Components sharing similar fill color |
| `text_regions` | object[] | OCR-extracted text regions (requires pytesseract) |
| `layout` | object | Overall layout metrics |
| `limitations` | string[] | Always present — describes what the tool cannot see |
| `ocr_available` | bool | Whether pytesseract was available during analysis |

### Image types

| Value | Description |
| ----- | ----------- |
| `architecture-diagram` | Light/white background with multiple rectangular components and connectors |
| `dashboard` | Many grid-like regions — monitoring tools, Grafana, etc. |
| `terminal` | Dark background with high text density (terminal output) |
| `ui-screenshot` | Light background, tall aspect ratio, structured UI regions |
| `unknown` | Could not classify — heuristics inconclusive |

### components[]

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | Stable within a single observation (`box_0`, `box_1`, ...) |
| `bbox` | float[4] | `[x1, y1, x2, y2]` in pixels |
| `area_percent` | float | Component area as % of image area |
| `label` | string\|null | Not set by heuristic detection; populated by downstream LLM |
| `fill_color` | string\|null | Dominant hex color of the box interior |
| `text` | string\|null | OCR text from inside the box; null without pytesseract |

### connections[]

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | string | Stable within a single observation (`edge_0`, `edge_1`, ...) |
| `direction` | string | `horizontal` / `vertical` / `diagonal` |
| `from_component` | string\|null | Nearest component id at the line start |
| `to_component` | string\|null | Nearest component id at the line end |

### groups[]

| Field | Type | Notes |
| ----- | ---- | ----- |
| `color` | string | Quantized hex color bucket shared by this group |
| `component_ids` | string[] | IDs of components in this group |
| `label` | string\|null | Not set by detection; populated by downstream LLM |

### text_regions[]

| Field | Type | Notes |
| ----- | ---- | ----- |
| `text` | string | OCR-extracted text string |
| `bbox` | float[4] | `[x1, y1, x2, y2]` in pixels |
| `confidence` | float | 0.0–1.0 pytesseract confidence |

### layout

| Field | Type | Notes |
| ----- | ---- | ----- |
| `width` | int | Image width in pixels |
| `height` | int | Image height in pixels |
| `component_count` | int | Number of detected components |
| `connection_count` | int | Number of detected connections |
| `dominant_flow` | string | `left-to-right` / `top-to-bottom` / `radial` / `unknown` |

---

## OCR

OCR is optional. Install pytesseract to enable:

```bash
brew install tesseract
pip install pytesseract
```

Without pytesseract:
- `text_regions` is always empty
- `component.text` is always `null`
- `ocr_available` is `false`
- A limitation entry is added explaining what is missing

---

## mq-mcp integration

The `visual_architecture_observation.v1` blob is designed to be passed as context
to mq-mcp review tools. The recommended integration pattern:

```
1. Run observe_architecture on the diagram
2. Pass the JSON output as `extra_context` to mq-mcp review_file or review_diff
3. mq-mcp uses component/connection topology as structural context for review
```

mq-mcp does not call `observe_architecture` directly — callers pass the result.
This is declared in `mq-mcp/docs/ORCHESTRATION_CONTRACT.md §5`.

---

## Limitations

Detection is fully heuristic (OpenCV contour analysis). The schema is designed to be
sparse rather than wrong — if a field cannot be determined, it is `null` rather than
guessed. Semantic interpretation (what a component represents, what the diagram means)
requires an LLM call and is not part of this schema.

The `limitations` field in every output lists what was not analyzed or what may be
inaccurate for the specific input image.

---

## Stability

Schema stable from v1.1.0. New top-level fields may be added in minor versions.
Field removals require a major version bump. Schema version is always present in output.
