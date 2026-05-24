# JSON Schema

Schema version: `mq-image.analysis.v1`

Produced by `mq-image analyze <image> --json`

---

## Two modes

### Summary mode (default)

```bash
mq-image analyze image.jpg --json
```

Unique object labels, no raw detections.
Confidence threshold: 0.25.

### Exhaustive mode

```bash
mq-image analyze image.jpg --exhaustive --json
mq-image analyze image.jpg --exhaustive --conf 0.05 --json
```

All detections preserved — duplicates, confidence, bbox, area.
Confidence threshold: 0.05 (unless `--conf` overrides).

---

## Summary shape

```json
{
  "objects": ["string"],
  "palette": ["#rrggbb"],
  "brightness": "dark | mid-tone | bright",
  "contrast": "low contrast | moderate contrast | high contrast",
  "depth": "shallow depth of field | moderate depth | deep / sharp throughout",
  "composition": "string",
  "symmetry": 0.0,
  "rule_of_thirds": 0.0,
  "prompt": "string",
  "mode": "summary",
  "detections": [],
  "limitations": ["string"],
  "text_regions": [],
  "unclassified_regions": [],
  "content_flags": {
    "nudity":          { "detected": false, "confidence": null },
    "full_nudity":     { "detected": false, "confidence": null },
    "sexual_activity": { "detected": false, "confidence": null },
    "source": "not_implemented",
    "note": "string"
  }
}
```

## Exhaustive shape

```json
{
  "objects": ["string"],
  "palette": ["#rrggbb"],
  "brightness": "dark | mid-tone | bright",
  "contrast": "low contrast | moderate contrast | high contrast",
  "depth": "shallow depth of field | moderate depth | deep / sharp throughout",
  "composition": "string",
  "symmetry": 0.0,
  "rule_of_thirds": 0.0,
  "prompt": "string",
  "mode": "exhaustive",
  "detections": [
    {
      "label": "string",
      "confidence": 0.0,
      "bbox": [0.0, 0.0, 0.0, 0.0],
      "area_percent": 0.0,
      "source_model": "yolov8n"
    }
  ],
  "limitations": ["string"],
  "text_regions": [],
  "unclassified_regions": [],
  "content_flags": {
    "nudity":          { "detected": false, "confidence": null },
    "full_nudity":     { "detected": false, "confidence": null },
    "sexual_activity": { "detected": false, "confidence": null },
    "source": "not_implemented",
    "note": "string"
  }
}
```

---

## Field reference

| Field | Type | Notes |
| ----- | ---- | ----- |
| `objects` | string[] | Unique labels; summary: highest-conf only; exhaustive: deduped from detections |
| `palette` | string[] | Hex colors, most dominant first |
| `brightness` | string | `dark` / `mid-tone` / `bright` |
| `contrast` | string | `low contrast` / `moderate contrast` / `high contrast` |
| `depth` | string | `shallow depth of field` / `moderate depth` / `deep / sharp throughout` |
| `composition` | string | Human-readable composition description |
| `symmetry` | float | 0.0–1.0 horizontal symmetry |
| `rule_of_thirds` | float | 0.0–1.0 alignment score |
| `prompt` | string | Reverse prompt string |
| `mode` | string | `summary` or `exhaustive` |
| `detections` | object[] | Raw detections; empty in summary mode |
| `detections[].confidence` | float | YOLOv8n confidence score |
| `detections[].bbox` | float[4] | `[x1, y1, x2, y2]` in pixels |
| `detections[].area_percent` | float | Detection area as % of image area |
| `detections[].source_model` | string | Model that produced the detection |
| `limitations` | string[] | Always present; describes what the tool cannot see |
| `text_regions` | object[] | OCR output — not yet implemented |
| `unclassified_regions` | object[] | Regions outside model classes — not yet implemented |

---

## No silent omission

`limitations` is always present. It explicitly states what the tool cannot see or did not analyze.

---

## Stability

Fields stable from v0.1.0. New fields may be added in minor versions. Field removals require major version bump.
