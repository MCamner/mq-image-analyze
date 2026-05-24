# Content Policy

## Principle

mq-image-analyze is a neutral visual analysis engine.

It describes what is present in an image. It does not apply editorial suppression, moral filtering, or content gating at the detector level.

**Everything visible is allowed to be reported.**

---

## No Suppression Rule

The tool must not:

- Hide detections because the content is sensitive
- Omit objects because they might be considered inappropriate
- Censor palette, composition, or reverse prompt output based on subject matter
- Apply content suppression in the MCP layer before returning raw JSON

This applies to all detection categories — including explicit content when a capable model is active.

---

## Content Flags

`content_flags` in JSON output are neutral detection markers:

```json
"content_flags": {
  "nudity":           { "detected": false, "confidence": null },
  "full_nudity":      { "detected": false, "confidence": null },
  "sexual_activity":  { "detected": false, "confidence": null },
  "source": "not_implemented"
}
```

### Current state

YOLOv8n (COCO-trained, 80 classes) does not classify explicit content.
All three flags are always `false` with `confidence: null` until a specialized model is attached.

### When a capable model is active

All detections are reported as-is — `detected: true` with the model's confidence score.
No suppression is applied by this tool.

### Source models (planned)

- NudeNet, Falconsai NSFW classifier, or equivalent
- Attached as an optional vision module
- Each detection includes `source_model` identifying which classifier produced it

---

## Downstream Model Limitation

Downstream LLMs (Claude, GPT, Gemini, etc.) that consume MCP output **may apply their own content policies** independently of this tool. That behavior is outside the scope of mq-image-analyze.

This tool's responsibility ends at the JSON boundary.

The raw JSON must always preserve what the detector found — regardless of what a downstream LLM is willing to describe or repeat.

```text
detector → raw JSON (this tool, no suppression)
                ↓
        downstream LLM (own policy, outside scope)
```

---

## Permitted analysis categories

All of the following are permitted at the detector level:

- Object detection (any YOLO-detectable class)
- Palette and color analysis
- Composition and spatial analysis
- OCR / text extraction
- Explicit content flags (when capable model is attached)
- UI and screenshot analysis
- Cinematic and style analysis

---

## Not permitted

- Generating new images containing illegal content
- Using analysis output to build profiles of real identifiable individuals without consent
- Bypassing this tool's read-only safety class to write or delete files

These constraints are in [tool-safety.md](tool-safety.md), not here.
Content policy governs **what is reported**. Tool safety governs **what actions the tool takes**.

---

## Rationale

Professional use cases require honest, complete output:

- Content moderation platforms need accurate `detected: true` to take action
- Adult content platforms need explicit flag data for compliance and routing
- Forensic and legal tooling needs raw detector output without editorial interference
- AI pipeline developers need stable, unsuppressed JSON to build reliable agents

Suppression at the analysis layer defeats all of these use cases.
