---
name: model-setup-maintainer
description: Use when changing mq-image-analyze model setup, YOLO weights, Ollama/OpenAI vision backends, doctor readiness checks, or model documentation.
---

# Model Setup Maintainer

Use this skill for local and cloud vision model readiness.

## Evals

### Should trigger

- "update the YOLO weights"
- "switch the Ollama vision backend"
- "doctor model readiness check fails"
- "document the OpenAI vision setup"

### Should not trigger

- "change MCP tools" → use `mcp-tools-maintainer`
- "change CLI flags" → use `cli-maintainer`
- "docs only" → use `docs-maintainer`

## Core Files

- `docs/model-setup.md`
- `mq_image_analyze/cli/doctor.py`
- `mq_image_analyze/vision/detection/detector.py`
- `mq_image_analyze/vision/semantic/provider.py`
- `mq_image_analyze/vision/semantic/ollama_vision.py`
- `mq_image_analyze/vision/semantic/openai_vision.py`
- `tests/test_doctor.py`
- `tests/test_semantic_provider.py`

## Model Contracts

Detection:

- YOLOv8n weights are expected locally.
- Model weights must not be committed.

Semantic vision modes:

- `local-fast` defaults to `bakllava` via Ollama.
- `local-deep` defaults to `llama3.2-vision` via Ollama.
- `cloud-verify` defaults to `gpt-4.1` via OpenAI.
- Use `gpt-4o` when specifically requested; do not invent `gpt-4.0`.

## Change Rules

- Keep doctor output clear about missing dependencies and model files.
- Keep model names consistent across README, CLI docs, and provider code.
- Do not require cloud credentials for local modes.
- Do not download or commit model weights automatically without explicit user
  request.

## Verification

```bash
python -m pytest tests/test_doctor.py tests/test_semantic_provider.py -q
mq-image doctor --json
```

For docs changes:

```bash
rg "local-fast|local-deep|cloud-verify|gpt-4.1|gpt-4o|bakllava" README.md docs mq_image_analyze
```
