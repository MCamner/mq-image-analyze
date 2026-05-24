#!/usr/bin/env bash
set -euo pipefail

echo "==> compileall"
python -m compileall mq_image_analyze -q

echo "==> pytest"
python -m pytest -q

echo "==> CLI entry point"
mq-image --help > /dev/null
mq-image --version

echo "==> OK"
