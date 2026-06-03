# Tool Safety

mq-image-analyze tools are read-first and non-destructive by default.

---

## Class A — Read-only image analysis

These tools read local image files and return structured analysis. They do not write, delete, or modify anything.

- `analyze_image`
- `extract_palette`
- `reverse_prompt`
- `analyze_ui`
- `observe_architecture`
- `image_ocr`

Rules:

- Must not write files
- Must not delete files
- Must not commit changes
- Must not call external APIs without explicit configuration

---

## Class B — Read-only comparison

These tools read two or more files and return structured comparison output.

- `compare_images`

Rules: same as Class A.

---

## Class C — Optional write-capable exports

Future tools may write reports or annotated images.

- `export_report`
- `annotate_image`

Rules:

- Never overwrite the original image by default
- Write only to an explicit output path
- Refuse ambiguous or relative paths that could resolve unexpectedly
- Never commit output files automatically

---

## Class D — Subprocess / model execution

Object detection runs a local model.

- `detect_objects` (YOLOv8n)

Rules:

- Model path must be explicit — no implicit fallback to remote download without user approval
- No shell execution triggered by image content
- No prompt injection via image metadata

---

## Boundary principle

Image analysis tools must never cross the line from **reading** to **acting**.

- Reading an image: always safe
- Writing a report: requires explicit output path
- Deleting or overwriting: never automatic
- Calling external services: requires explicit configuration
