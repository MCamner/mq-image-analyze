---
name: visual-reasoning
description: Use when analyzing an image for objects, palette, composition, mood, visual hierarchy, and prompt intent.
phase: 1
status: available
---

# Visual Reasoning

Use this skill when the user wants to understand what an image contains and why
it works visually.

## Core workflow

1. Inspect image metadata (format, resolution)
2. Detect objects (YOLOv8n)
3. Extract dominant palette
4. Estimate brightness and contrast
5. Analyze composition (rule-of-thirds, symmetry, visual weight, depth)
6. Generate structured reverse prompt
7. Return both human-readable and JSON output

## Inputs

- `image_path` — local path to image file (jpg, png, webp)
- `output_format` — `text` (default) or `json`

## Outputs

- `objects` — detected labels with confidence
- `palette` — dominant hex colors
- `brightness` — dark / mid-tone / bright
- `contrast` — low / moderate / high
- `depth` — shallow / moderate / deep
- `composition` — balance, alignment, symmetry score
- `reverse_prompt` — single-string prompt reconstructed from signals

## Prefer

- Deterministic output — same image, same result
- Explainable labels — no vague descriptions
- Compact summaries — useful in agent context windows
- JSON contracts — stable shape for integrations

## Avoid

- Generating new images
- Making unverifiable aesthetic claims
- Overwriting source files
- External API calls without explicit configuration
