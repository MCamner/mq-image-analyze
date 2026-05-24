# mq-image-analyze

Visual reasoning infrastructure — not a model storage repo.

## What this is

Orchestration + intelligence layer for image analysis.
Models are replaceable dependencies, not part of the system.

## Flow

```text
image → vision analysis → reasoning → structured output
```

## Usage

```bash
mq-image analyze image.png
```

Example output:

```text
Objects:    person, monitor, terminal
Style:      cinematic dark UI, minimal contrast palette
Composition: centered hierarchy, shallow visual depth
Reverse prompt: low-key lighting, matte blacks, subtle bloom
```

## Structure

```text
mq_image_analyze/   core library
tests/              test suite
configs/            model + pipeline configs
scripts/            dev tooling
docs/               architecture + decisions
examples/           usage examples
models/             local model weights (gitignored)
```

## Models

Models are not committed. Install with:

```bash
mq-image models install yolov8n
```

## Status

Early prototype.
