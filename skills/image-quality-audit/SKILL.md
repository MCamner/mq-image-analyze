---
name: image-quality-audit
description: Use when scoring an image for composition quality, clarity, and visual hierarchy.
phase: 2
status: available
---

# Image Quality Audit

Use this skill to produce numeric quality scores for an image.

## Evals

### Should trigger

- "score this image's composition"
- "rate the visual hierarchy of this photo"
- "is this image well composed?"
- "grade the clarity of this render"

### Should not trigger

- "turn this image into a prompt" → use `reverse-prompt`
- "review this app screenshot for usability" → use `screenshot-ui-review`
- "what objects are in this image?" → use `visual-reasoning`

## Core workflow

1. Run visual-reasoning pipeline
2. Score each dimension independently
3. Compute overall score
4. Return structured score report

## Scores (0.0 – 1.0)

| Dimension | What it measures |
| --------- | ---------------- |
| `composition_score` | Rule-of-thirds alignment, balance, visual weight |
| `clarity_score` | Sharpness, depth coherence, noise level |
| `visual_hierarchy_score` | Clear subject, supporting elements, background |
| `style_consistency` | Palette coherence, tonal consistency |
| `overall` | Weighted average |

## Output

```json
{
  "composition_score": 0.0,
  "clarity_score": 0.0,
  "visual_hierarchy_score": 0.0,
  "style_consistency": 0.0,
  "overall": 0.0,
  "notes": ["string"]
}
```

## Use cases

- Comparing generated image batches
- Flagging low-quality outputs before delivery
- Detecting style drift across a series
