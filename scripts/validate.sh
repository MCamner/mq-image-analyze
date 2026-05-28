#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Prefer venv binaries if available
PYTHON="${REPO_ROOT}/.venv/bin/python"
MQ_IMAGE="${REPO_ROOT}/.venv/bin/mq-image"
[[ -x "$PYTHON" ]]   || PYTHON="python"
[[ -x "$MQ_IMAGE" ]] || MQ_IMAGE="mq-image"

echo "==> compileall  ($PYTHON)"
"$PYTHON" -m compileall mq_image_analyze -q

echo "==> pytest"
"$PYTHON" -m pytest -q

echo "==> CLI entry point"
"$MQ_IMAGE" --help > /dev/null
"$MQ_IMAGE" --version

echo "==> OK"
