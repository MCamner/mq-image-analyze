# Tool Safety

mq-image-analyze tools are read-first and non-destructive by default.

---

## Class A — Local read-only image analysis

These tools read local images and return analysis without file modifications.

- `extract_palette`
- `analyze_ui`
- `observe_architecture`
- `image_ocr`
- `image_perception`

## Class B — Read-only external-capable analysis or comparison

- `analyze_image`
- `reverse_prompt`
- `compare_images`

These tools do not write or delete image files. `analyze_image` and
`reverse_prompt` may send images to OpenAI only when the operator explicitly
selects `vision_mode=cloud-verify` (the default remains `local-fast`).
`compare_images` is classified B by the operator's ADR-003 decision;
this classification alone does not enable a remote call. Class B metadata
does not authorize implicit uploads or change runtime defaults.

Rules for both A and B:

- Must not write, delete or commit files
- Must not call external APIs without explicit configuration
- Keep remote vision opt-in; do not fall back silently to cloud services

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

## Path confinement

By default the MCP tools read any image file the server process can read. Set
`MQ_IMAGE_ALLOWED_ROOTS` to confine them:

```bash
export MQ_IMAGE_ALLOWED_ROOTS="$HOME/screenshots:$HOME/repos/diagrams"
```

- Separator is `:` on macOS/Linux (`;` on Windows).
- Paths are resolved before the check, so `..` and symlinks cannot lead outside a root.
- A path outside every root raises `PermissionError` before the file is checked for
  existence, so the error does not reveal what is on disk.
- Applies to all MCP tools. The CLI is not confined: it runs as the user who typed the command.

---

## Boundary principle

Image analysis tools must never cross the line from **reading** to **acting**.

- Reading an image: always safe
- Writing a report: requires explicit output path
- Deleting or overwriting: never automatic
- Calling external services: requires explicit configuration
