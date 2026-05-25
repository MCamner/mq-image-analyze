---
name: screenshot-ui-review
description: Use when reviewing screenshots of apps, terminals, dashboards, websites, or GitHub pages for layout and usability.
phase: 3
status: available
---

# Screenshot UI Review

Use this skill for visual critique of UI screenshots.

## Core workflow

1. Detect UI regions (OCR, layout segmentation)
2. Identify visual hierarchy
3. Check spacing, contrast, alignment
4. Flag accessibility concerns
5. Return structured review

## What to check

- Visual hierarchy — is the most important element clear?
- Spacing — consistent rhythm or crowded?
- Contrast — readable text at all sizes?
- Alignment — grid discipline?
- Density — too much or too little information?
- Readability — fonts, sizes, line lengths?
- Call-to-action clarity — obvious next step?
- Terminal / CLI polish when reviewing developer tools

## Output

- What works well
- What is confusing or weak
- High-impact fixes (ordered by priority)
- Suggested next iteration direction

## Avoid

- Aesthetic opinions without reasoning
- Prescribing specific design tools
- Generating replacement UI without approval
