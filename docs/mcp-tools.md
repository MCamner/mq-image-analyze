# MCP Tools

All tools are deterministic, explainable, structured, and composable.

---

## analyze_image

Full image analysis pipeline.

```python
analyze_image(image_path: str, output_format: "text" | "json" = "json")
```

Output:

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

## extract_palette

Dominant color palette from an image.

```python
extract_palette(image_path: str, n_colors: int = 6)
```

Output: list of hex color strings, most dominant first.

---

## extract_style

Visual style classification.

```python
extract_style(image_path: str)
```

Output:

```json
{
  "style": "cinematic | documentary | ui | illustration | photograph",
  "confidence": 0.0,
  "signals": ["string"]
}
```

---

## reverse_prompt

Generate a text prompt that would recreate the image's visual character.

```python
reverse_prompt(image_path: str)
```

Output: string prompt.

---

## compare_images

Compare two images for style and composition similarity.

```python
compare_images(image_a: str, image_b: str)
```

Output:

```json
{
  "palette_similarity": 0.0,
  "composition_similarity": 0.0,
  "style_match": true,
  "differences": ["string"]
}
```

---

## score_image

Numeric quality scores for composition and visual clarity.

```python
score_image(image_path: str)
```

Output:

```json
{
  "composition_score": 0.0,
  "clarity_score": 0.0,
  "visual_hierarchy_score": 0.0,
  "overall": 0.0
}
```

---

## analyze_ui

Screenshot / UI-specific analysis.

```python
analyze_ui(image_path: str)
```

Output:

```json
{
  "layout": "string",
  "design_language": "string",
  "color_scheme": "string",
  "text_regions": [{"bbox": [], "content": "string"}],
  "ui_elements": ["string"],
  "accessibility_flags": ["string"]
}
```

---

## ocr_image

Extract visible text from an image.

```python
ocr_image(image_path: str, language: str = "en")
```

Output: list of `{text, confidence, bbox}` objects.
