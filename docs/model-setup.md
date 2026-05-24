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

---

## Future model management

v0.1.1 goal: `mq-image models install yolov8n` CLI command.
