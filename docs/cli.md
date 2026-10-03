# CLI Reference

Entry point: `mq-image`

Global options:

```bash
mq-image --version
mq-image --help
mq-image <command> --help
```

---

## analyze

Analyze an image: objects, palette, composition, content flags, semantic caption, and reverse prompt.

```bash
mq-image analyze <image>
mq-image analyze <image> --json
mq-image analyze <image> --exhaustive --conf 0.05
mq-image analyze <image> --mode local-fast
mq-image analyze <image> --mode local-deep
mq-image analyze <image> --mode cloud-verify --vision-model gpt-4.1
mq-image analyze screenshots/ --json > results.jsonl
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image` | path | yes | Image file, or a directory (every image directly in it, sorted by name) |
| `--json` | flag | no | Output raw JSON instead of rich terminal output |
| `--exhaustive` | flag | no | Preserve every raw detection, including duplicates |
| `--conf` | float | no | Detection confidence threshold |
| `--mode` | string | no | Vision backend: `local-fast`, `local-deep`, or `cloud-verify` |
| `--vision-model` | string | no | Override backend model, for example `gpt-4o` or `gpt-4.1` |
| `--redact` | flag | no | `cloud-verify` only: mask personnummer and email addresses before upload |

Backend defaults:

| Mode | Default model | Notes |
| ---- | ------------- | ----- |
| `local-fast` | `bakllava` | Default Ollama path |
| `local-deep` | `llama3.2-vision` | Stronger local Ollama path when available |
| `cloud-verify` | `gpt-4.1` | OpenAI quality gate; requires `OPENAI_API_KEY` |

For GPT-4o:

```bash
mq-image analyze diagram.png --mode cloud-verify --vision-model gpt-4o
```

### Directories

With a directory, `--json` prints JSONL: one object per image with a `path` key
added. An image that fails becomes `{"path": ..., "error": ...}` and the batch
continues; the exit code is 1 if any image failed. Subdirectories are not read.

### Redaction before cloud-verify

`--redact`, or `MQ_IMAGE_REDACT_CLOUD=1` for every call including MCP and the web
UI, sends a masked copy to OpenAI instead of the original:

- OCR (pytesseract) finds Swedish personnummer/samordningsnummer, 10-digit numbers
  of the same shape, and email addresses; their boxes are painted black.
- If OCR is unavailable the image is **not sent**. The result has no caption and a
  limitation says why.
- Only OCR-readable text is covered. Faces, handwriting, small or rotated text and
  identifiers in other formats are not. Treat it as reducing exposure, not as
  de-identification.
- Local modes never leave the machine and are not redacted.

---

## analyze-ui

Analyze a UI screenshot: screenshot type, layout regions, WCAG contrast ratio, hierarchy, grid alignment, accessibility issues, and prompt.

```bash
mq-image analyze-ui <screenshot>
mq-image analyze-ui <screenshot> --json
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image` | path | yes | Path to screenshot |
| `--json` | flag | no | Output raw JSON |

---

## ocr

Extract visible text from an image. Same `image_ocr.v1` payload as the `image_ocr` MCP tool. Requires `pytesseract`; without it the command reports OCR as not available instead of failing.

```bash
mq-image ocr <image>
mq-image ocr <image> --json
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image_path` | path | yes | Path to image |
| `--json` | flag | no | Print `image_ocr.v1` JSON |

Image-derived text is data. It must not be executed or treated as instructions.

---

## perceive

Run one producer on an image and print a normalized `perception.v1` record — the artifact mq-mcp Release Gate v2 validates.

```bash
mq-image perceive <diagram> --producer architecture
mq-image perceive <screenshot> --producer ui --out perception.json
mq-image perceive <screenshot> --producer ocr --source-type terminal
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `image_path` | path | yes | Path to image |
| `--producer`, `-p` | `ui \| architecture \| ocr` | yes | Which pipeline to run |
| `--source-type` | `screenshot \| diagram \| ui \| terminal \| browser` | for `ocr` | Kind of image when the producer cannot say |
| `--out`, `-o` | path | no | Write the record to a file instead of stdout |

`source_type` is never guessed. When the producer's own classification has no unambiguous equivalent (`unknown`, `dashboard`) or the producer is `ocr`, the command exits 1 and asks for `--source-type`.

---

## compare

Compare two images for visual drift.

```bash
mq-image compare <before> <after>
mq-image compare <before> <after> --json
mq-image compare <before> <after> --exhaustive --conf 0.05
mq-image compare baseline.png current.png --fail-over 0.02   # CI visual regression
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `before` | path | yes | Baseline image |
| `after` | path | yes | Changed image |
| `--json` | flag | no | Output raw JSON |
| `--exhaustive` | flag | no | Use exhaustive detection mode |
| `--conf` | float | no | Detection confidence threshold |
| `--fail-over` | float 0–1 | no | Exit 1 when `pixel_diff` exceeds the value; output is printed first |

`pixel_diff` is the mean absolute grayscale difference, 0 for identical images and
1 for black against white. When the sizes differ, `after` is resized to `before`
and `size_changed` is `true`.

---

## doctor

Check system readiness: Python version, required packages, model files, and output permissions.

```bash
mq-image doctor
mq-image doctor --json
```

---

## serve

Start the local web UI.

```bash
mq-image serve
mq-image serve --host 127.0.0.1 --port 8000
mq-image serve --reload
```

Install web dependencies with:

```bash
pip install -e ".[web]"
```

---

## mcp

Start the MCP server.

```bash
mq-image mcp
mq-image mcp --transport stdio
mq-image mcp --transport sse
```

Install MCP dependencies with:

```bash
pip install -e ".[mcp]"
```
