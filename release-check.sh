#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Prefer venv binaries if available
PYTHON="${REPO_ROOT}/.venv/bin/python"
MQ_IMAGE="${REPO_ROOT}/.venv/bin/mq-image"
[[ -x "$PYTHON" ]]   || PYTHON="python"
[[ -x "$MQ_IMAGE" ]] || MQ_IMAGE="mq-image"

ERRORS=0

fail() { echo "FAIL: $1"; ERRORS=$((ERRORS + 1)); }
ok()   { echo "  ok: $1"; }

echo "==> Release check"
echo ""

# Git state
if [[ -n "$(git status --porcelain)" ]]; then
  fail "Uncommitted changes present"
else
  ok "Git working tree clean"
fi

# VERSION
if [[ ! -f VERSION ]]; then
  fail "VERSION file missing"
else
  VERSION=$(cat VERSION)
  ok "VERSION = $VERSION"
fi

# CHANGELOG mentions current version
if ! grep -q "$VERSION" CHANGELOG.md 2>/dev/null; then
  fail "CHANGELOG.md does not mention version $VERSION"
else
  ok "CHANGELOG.md mentions $VERSION"
fi

# pyproject version matches VERSION
PYPROJECT_VERSION=$("$PYTHON" - <<'PY'
import tomllib
from pathlib import Path

data = tomllib.loads(Path("pyproject.toml").read_text())
print(data["project"]["version"])
PY
)
if [[ "$PYPROJECT_VERSION" != "$VERSION" ]]; then
  fail "pyproject.toml version $PYPROJECT_VERSION does not match VERSION $VERSION"
else
  ok "pyproject.toml version matches VERSION"
fi

# README exists and is non-empty
if [[ ! -s README.md ]]; then
  fail "README.md missing or empty"
else
  ok "README.md present"
fi

# Docs
for doc in docs/architecture.md docs/cli.md docs/json-schema.md docs/mcp-tools.md docs/tool-safety.md; do
  if [[ ! -f "$doc" ]]; then
    fail "$doc missing"
  else
    ok "$doc present"
  fi
done

# Tests pass
echo ""
echo "==> Running tests"
if "$PYTHON" -m pytest -q 2>&1; then
  ok "Tests pass"
else
  fail "Tests failed"
fi

# CLI works
echo ""
echo "==> CLI checks"
if "$MQ_IMAGE" --help > /dev/null 2>&1; then
  ok "mq-image --help"
else
  fail "mq-image --help failed"
fi

if "$MQ_IMAGE" --version > /dev/null 2>&1; then
  ok "mq-image --version"
else
  fail "mq-image --version failed"
fi

# No model weights committed
if git ls-files | grep -qE '\.(pt|ckpt|safetensors|bin|gguf|onnx)$'; then
  fail "Model weight files are tracked in git"
else
  ok "No model weights in git"
fi

# No .env committed
if git ls-files | grep -q '\.env'; then
  fail ".env file tracked in git"
else
  ok "No .env in git"
fi

echo ""
if [[ $ERRORS -eq 0 ]]; then
  echo "Release check passed. Ready to tag v$VERSION."
else
  echo "$ERRORS check(s) failed. Fix before releasing."
  exit 1
fi
