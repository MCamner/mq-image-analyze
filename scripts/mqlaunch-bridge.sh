#!/usr/bin/env bash
# mqlaunch bridge for mq-image-analyze
# Usage: mqlaunch-bridge.sh <command> [args...]
# Commands: analyze, analyze-ui, compare, mcp, doctor
#
# Add to mqlaunch by sourcing or linking:
#   ln -sf ~/mq-image-analyze/scripts/mqlaunch-bridge.sh ~/bin/mq-image-launch

set -euo pipefail

REPO_DIR="${MQ_IMAGE_DIR:-$HOME/mq-image-analyze}"
VENV="$REPO_DIR/.venv/bin/activate"

if [[ ! -f "$VENV" ]]; then
  echo "[mq-image] venv not found at $REPO_DIR/.venv — run: cd $REPO_DIR && python -m venv .venv && pip install -e '.[web,mcp]'" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV"

CMD="${1:-help}"
shift || true

case "$CMD" in
  analyze|a)
    mq-image analyze "$@"
    ;;
  analyze-ui|ui)
    mq-image analyze-ui "$@"
    ;;
  compare|diff)
    mq-image compare "$@"
    ;;
  mcp)
    mq-image mcp "$@"
    ;;
  serve|web)
    mq-image serve "$@"
    ;;
  doctor|check)
    mq-image doctor
    ;;
  help|--help|-h|"")
    mq-image --help
    ;;
  *)
    echo "[mq-image] Unknown command: $CMD" >&2
    echo "Available: analyze, analyze-ui, compare, mcp, serve, doctor" >&2
    exit 1
    ;;
esac
