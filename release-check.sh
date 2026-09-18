#!/usr/bin/env bash
# Release readiness check for mq-image-analyze. Read-only.
#
# Human mode (no flags / --dry-run): prints per-check ok/FAIL, exits 1 on any
#   failure. --dry-run skips the clean-git-tree requirement.
# Contract mode (--json): emits a repo_release_check.v1 object on stdout and
#   exits 0 (the `status` field carries the verdict). Consumed by mq-agent's
#   `stack release --all --preflight`. --json implies --dry-run (the preflight
#   owns the dirty-tree check).
# Model/example generation and tag publication remain explicitly CI-only;
# scripts/check-gate-parity.py documents why READY does not cover them.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT" || exit 1

DRY_RUN=0
JSON=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --json) JSON=1 ;;
    *) echo "usage: ./release-check.sh [--dry-run] [--json]" >&2; exit 2 ;;
  esac
done
[[ "$JSON" -eq 1 ]] && DRY_RUN=1

# Prefer venv binaries if available
PYTHON="${REPO_ROOT}/.venv/bin/python"
MQ_IMAGE="${REPO_ROOT}/.venv/bin/mq-image"
[[ -x "$PYTHON" ]]   || PYTHON="python"
[[ -x "$MQ_IMAGE" ]] || MQ_IMAGE="mq-image"

BLOCKERS=()
say()  { [[ "$JSON" -eq 1 ]] || echo "$1"; }
ok()   { [[ "$JSON" -eq 1 ]] || echo "  ok: $1"; }
fail() { BLOCKERS+=("$1"); [[ "$JSON" -eq 1 ]] || echo "FAIL: $1" >&2; }

# run LABEL CMD...  — record a blocker on failure; keep stdout clean by routing
# captured output to stderr (human mode) only on failure.
run() {
  local label="$1"; shift
  local out
  if out="$("$@" 2>&1)"; then
    ok "$label"
  else
    fail "$label"
    [[ "$JSON" -eq 1 ]] || printf '%s\n' "$out" >&2
  fi
}

say "==> Release check"

# Git state (skipped in --dry-run/preflight — the caller owns the dirty check)
if [[ "$DRY_RUN" -eq 0 ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    fail "Uncommitted changes present"
  else
    ok "Git working tree clean"
  fi
fi

VERSION=""
if [[ ! -f VERSION ]]; then
  fail "VERSION file missing"
else
  VERSION="$(cat VERSION)"
  ok "VERSION = $VERSION"
fi

if [[ -n "$VERSION" ]] && ! grep -q "$VERSION" CHANGELOG.md 2>/dev/null; then
  fail "CHANGELOG.md does not mention version $VERSION"
elif [[ -n "$VERSION" ]]; then
  ok "CHANGELOG.md mentions $VERSION"
fi

PYPROJECT_VERSION="$("$PYTHON" - <<'PY' 2>/dev/null
import tomllib
from pathlib import Path
print(tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"])
PY
)"
if [[ "$PYPROJECT_VERSION" != "$VERSION" ]]; then
  fail "pyproject.toml version '$PYPROJECT_VERSION' != VERSION '$VERSION'"
else
  ok "pyproject.toml version matches VERSION"
fi

if [[ ! -s README.md ]]; then
  fail "README.md missing or empty"
else
  ok "README.md present"
fi

for doc in docs/architecture.md docs/cli.md docs/json-schema.md docs/mcp-tools.md docs/tool-safety.md; do
  if [[ ! -f "$doc" ]]; then
    fail "$doc missing"
  else
    ok "$doc present"
  fi
done

say "==> Running tests"
run "pytest" "$PYTHON" -m pytest -q

say "==> CLI checks"
run "mq-image --help" "$MQ_IMAGE" --help
run "mq-image --version" "$MQ_IMAGE" --version
run "mq-image mcp --help" "$MQ_IMAGE" mcp --help

run "compileall mq_image_analyze" "$PYTHON" -m compileall -q mq_image_analyze
run "MCP sample payloads match live tool contracts" "$PYTHON" scripts/check-mcp-sample-payloads.py

say "==> Agent discovery and CI parity"
run "check-skills.sh" bash scripts/check-skills.sh
run "check-gate-parity.py" "$PYTHON" scripts/check-gate-parity.py

if git ls-files | grep -qE '\.(pt|ckpt|safetensors|bin|gguf|onnx)$'; then
  fail "Model weight files are tracked in git"
else
  ok "No model weights in git"
fi

if git ls-files | grep -q '\.env'; then
  fail ".env file tracked in git"
else
  ok "No .env in git"
fi

# CI runs markdownlint as its own required workflow, so a release-check that
# skips it can report "Ready to tag" on a tree CI will reject — which is
# exactly what happened to v1.5.0. No globs are passed: the action and this
# both read .markdownlint-cli2.jsonc, and adding a glob here would widen the
# set CI actually lints. Unrunnable is a failure, not a pass: a gate that
# could not be checked has not been checked.
say "==> Markdown checks"
if command -v npx >/dev/null 2>&1; then
  run "markdownlint" npx --yes markdownlint-cli2
else
  fail "markdownlint not runnable (npx not found) — CI runs it as a required check"
fi

if [[ "$JSON" -eq 1 ]]; then
  status=READY
  [[ "${#BLOCKERS[@]}" -gt 0 ]] && status=BLOCKED
  "$PYTHON" - "$status" "$VERSION" ${BLOCKERS[@]+"${BLOCKERS[@]}"} <<'PY'
import json
import sys

status, version, *blockers = sys.argv[1:]
print(json.dumps({
    "schema": "repo_release_check.v1",
    "repo": "mq-image-analyze",
    "status": status,
    "blockers": blockers,
    "warnings": [],
    "evidence": {"version": version},
}))
PY
  exit 0
fi

echo ""
if [[ "${#BLOCKERS[@]}" -eq 0 ]]; then
  echo "Release check passed. Ready to tag v$VERSION."
else
  echo "${#BLOCKERS[@]} check(s) failed. Fix before releasing."
  exit 1
fi
