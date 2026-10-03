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
| `--cache` | flag | no | Reuse semantic captions from a local cache |

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

### Caption cache

`--cache` stores semantic captions under `$MQ_IMAGE_CACHE_DIR`, default
`~/.cache/mq-image-analyze/captions`. The key is the image content, vision mode,
model, whether the upload was redacted, and the prompt text, so renaming a file
still hits while changing any of the others misses. Missing captions are not
stored. Delete the directory to clear it. The MCP tools never use the cache,
so they keep writing nothing to disk.

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

## regress

Visual regression: a directory of approved screenshots against a new run. Screens
are paired by file name.

```bash
mq-image regress baseline/ current/
mq-image regress baseline/ current/ --out reports/perception/regress
mq-image regress baseline/ current/ --fail-over 0.001 --json
mq-image regress baseline/ current/ --ignore-region 520,0,639,56 --ignore-region login.png:0,360,300,399
mq-image regress baseline/ current/ --update-baseline
```

| Argument | Type | Required | Description |
| -------- | ---- | -------- | ----------- |
| `baseline` | directory | yes | Approved screenshots |
| `current` | directory | yes | New screenshots, same file names |
| `--fail-over` | float 0–1 | no | Share of changed pixels a screen may have. Default `0`: any change that survives noise filtering fails |
| `--out`, `-o` | directory | no | Write `report.jsonl`, `report.html`, `overlays/` and one `perception.v1` artifact per failing screen |
| `--source-type` | string | no | `source_type` for the artifacts. Default `screenshot` |
| `--ignore-region` | `[name:]x1,y1,x2,y2` | no | Exclude a box (baseline pixels, inclusive) from comparison, for every screen or only `name`. Repeatable |
| `--json` | flag | no | Print JSONL, one line per screen |
| `--update-baseline` | flag | no | Copy every current screenshot into the baseline and exit 0. Nothing is deleted |

How a screen is judged:

| Status | When | Fails |
| ------ | ---- | ----- |
| `unchanged` | No region of changed pixels survives the noise filter, or the changed share is within `--fail-over` | no |
| `changed` | Changed share exceeds `--fail-over`, or the image size changed | yes |
| `missing` | In baseline, not in current | yes |
| `new` | In current, not in baseline | no |

A pixel counts as changed when its grayscale value differs by more than 25 of 255,
so anti-aliasing and compression noise do not count. The threshold is on the share
of changed pixels rather than the mean `pixel_diff`, because a renamed button moves
the mean by about 0.001.

Exit code 1 when any screen fails. That exit code is what blocks CI: mq-mcp's
Release Gate validates the artifacts and lists their `risk_signals` as a warning,
but does not block on them. Write the artifacts under `reports/perception/` for
the gate to find them.

Ignored regions are for content that changes on every run, such as clocks, dates,
user names and session IDs. Pixels inside them never count as changed. They are
listed per screen as `ignored_regions` in the JSON and drawn grey in the overlays.
A bad box is a usage error (exit 2).

This is pixel comparison. It says where a screen changed, not whether the change
was intended.

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
mq-image mcp --transport http --port 8766
```

Install MCP dependencies with:

```bash
pip install -e ".[mcp]"
```

The HTTP transport is the loopback bridge used by mq-agent. Its default port is
8766; stdio remains the default transport.
