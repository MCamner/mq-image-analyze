---
name: reverse-prompt
description: Use when turning an image into a reusable prompt for image generation, visual design, or cinematic direction.
phase: 1
status: available
---

# Reverse Prompt

Use this skill to convert an image into a structured prompt that captures its
visual character.

## Core workflow

1. Run visual-reasoning on the image
2. Extract subject, environment, lighting, palette, composition
3. Translate signals into prompt language
4. Return single-string prompt and token list

## Inputs

- `image_path` — local path to image file

## Outputs

- `prompt` — complete prompt string
- `tokens` — individual prompt components

## Include in prompt

- Subject / objects
- Environment and setting
- Palette description
- Lighting (inferred from brightness + contrast)
- Composition style
- Depth / focus treatment
- Mood and tone

## Avoid

- Claiming exact camera or lens data unless EXIF confirms it
- Overfitting prompt language to a single model provider
- Hallucinated details not visible in the image
