# JSON Schema

Schema version: `mq-image.analysis.v1`

Produced by `mq-image analyze <image> --json`

---

## Shape

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
  "prompt": "string"
}
```

---

## Field reference

| Field | Type | Values |
| ----- | ---- | ------ |
| `objects` | string[] | YOLOv8n class labels, sorted by confidence |
| `palette` | string[] | Hex colors, most dominant first |
| `brightness` | string | `dark` / `mid-tone` / `bright` |
| `contrast` | string | `low contrast` / `moderate contrast` / `high contrast` |
| `depth` | string | `shallow depth of field` / `moderate depth` / `deep / sharp throughout` |
| `composition` | string | Human-readable composition description |
| `symmetry` | float | 0.0–1.0, horizontal symmetry score |
| `rule_of_thirds` | float | 0.0–1.0, rule-of-thirds alignment score |
| `prompt` | string | Reverse prompt string |

---

## Example

```json
{
  "objects": ["person", "monitor", "terminal"],
  "palette": ["#0a0a0f", "#1c1f2e", "#3a4a6b", "#c8d4e8", "#f0f4ff", "#2a3550"],
  "brightness": "dark",
  "contrast": "moderate contrast",
  "depth": "shallow depth of field",
  "composition": "centered, rule-of-thirds alignment",
  "symmetry": 0.871,
  "rule_of_thirds": 0.453,
  "prompt": "person, monitor, terminal, dark scene, moderate contrast, shallow depth of field, color palette: #0a0a0f, #1c1f2e, #3a4a6b, centered, rule-of-thirds alignment"
}
```

---

## Stability guarantee

Fields in this schema are stable from v0.1.0 onward.
New fields may be added in minor versions.
Field removals require a major version bump.
