# Model Setup

Models are replaceable dependencies — they are not committed to the repository.

---

## YOLOv8n

Object detection model used by `vision/detection`.

### Placement

```text
models/yolov8n.pt
```

### Download

```bash
# Option 1: Ultralytics auto-download on first run
mq-image analyze image.jpg   # downloads if models/yolov8n.pt is absent

# Option 2: Manual download
cd models/
curl -L https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt -o yolov8n.pt
```

### Verify

```bash
mq-image doctor
```

Doctor will confirm the model file is present and loadable.

---

## Vision backend (Ollama / OpenAI)

Semantic captions, OCR and diagram interpretation use a vision model selected by `--mode`.
Defaults live in [mq_image_analyze/vision/semantic/provider.py](../mq_image_analyze/vision/semantic/provider.py).

| Mode | Default model | Requires |
| ---- | ------------- | -------- |
| `local-fast` | `qwen3.5:9b` | Ollama on `localhost:11434` |
| `local-deep` | `qwen3.5:9b` | Ollama on `localhost:11434` |
| `cloud-verify` | `gpt-4.1` | `OPENAI_API_KEY` |

Both local modes currently select the same model; the names are kept for compatibility.
`--vision-model` overrides the default.

### Install (local)

```bash
ollama pull qwen3.5:9b
ollama list            # confirm qwen3.5:9b is present
```

A local failure is reported in the result without calling OpenAI.
Cloud analysis only runs with an explicit `--mode cloud-verify`.

`mq-image doctor` checks Python, imports, the YOLO model file and output permissions.
It does not check Ollama or the vision model — use `ollama list`.

---

## OCR (Tesseract)

Used by `ocr`, `regress` text checks, `observe-architecture` box labels and
`--redact`. Optional: not in `pyproject.toml` dependencies.

```bash
brew install tesseract tesseract-lang   # engine + language data (incl. Swedish)
pip install pytesseract
```

Without it, OCR reports `ocr_available: false` and a limitation instead of failing.
Language selection is described in [cli.md](cli.md#text-in-changed-regions).

---

## Model directory

```text
models/      gitignored
             not committed to source control
             install per-machine
```

Never commit `.pt`, `.ckpt`, `.safetensors`, `.bin`, `.gguf`, or `.onnx` files.

---

## Replacing the model

The detector is loaded from a single path in [mq_image_analyze/vision/detection/detector.py](../mq_image_analyze/vision/detection/detector.py).

To use a different YOLO variant:

1. Place the model in `models/`
2. Update `_MODEL_PATH` in `detector.py`
3. Run `mq-image doctor` to verify
