#!/usr/bin/env python3
"""Static, read-only mapping of image-analyze release checks to PR CI."""
from __future__ import annotations

import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CI_ONLY = {
    "examples.yml": "CI-only: generates sample images/model output and auto-commits on push to main; cannot run in read-only preflight.",
    "release.yml": "CI-only: tag-triggered publication is downstream of release readiness.",
}
STEPS = {
    "tests.yml": ["Set up Python ${{ matrix.python-version }}", "Install dependencies",
                  "Check imports", "Run tests", "Verify CLI entry point", "Check skills consistency"],
    "markdownlint.yml": [],  # Action-based workflow has no named steps.
    "gate-parity.yml": ["Checkout", "Validate gate parity", "Test parity failures",
                        "Set up Python", "Install dependencies", "Run release preflight"],
}
CI_COMMANDS = {
    "tests.yml": ["python-version: [\"3.11\", \"3.12\"]", "-c constraints.txt",
                  "import mq_image_analyze", "pytest tests/ -v --tb=short", "mq-image --help",
                  "bash scripts/check-skills.sh"],
    "markdownlint.yml": ["DavidAnson/markdownlint-cli2-action@v20", 'globs: "**/*.md"'],
    "gate-parity.yml": ["python3 scripts/check-gate-parity.py", "--self-test",
                        "./release-check.sh --json"],
}
LOCAL_COMMANDS = {
    "tests": 'run "pytest" "$PYTHON" -m pytest -q',
    "CLI": 'run "mq-image --help" "$MQ_IMAGE" --help',
    "markdownlint": 'run "markdownlint" npx --yes markdownlint-cli2',
    "skills": 'run "check-skills.sh" bash scripts/check-skills.sh',
    "parity": 'run "check-gate-parity.py" "$PYTHON" scripts/check-gate-parity.py',
}


def verify(root: Path) -> list[str]:
    errors: list[str] = []
    workflows = root / ".github" / "workflows"
    files = {p.name for p in workflows.glob("*.yml")} | {p.name for p in workflows.glob("*.yaml")}
    expected = set(STEPS) | set(CI_ONLY)
    for name in sorted(files - expected):
        errors.append(f"unregistered workflow: {name}")
    for name in sorted(expected - files):
        errors.append(f"registered workflow missing: {name}")
    for name, reason in CI_ONLY.items():
        if not reason.startswith("CI-only:") or len(reason) < 30:
            errors.append(f"CI-only rationale missing: {name}")
    for name, expected_steps in STEPS.items():
        path = workflows / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        actual = re.findall(r"^\s*- name:\s*(.+?)\s*$", text, re.M)
        if Counter(actual) != Counter(expected_steps):
            errors.append(f"CI steps changed: {name}: {actual!r}")
        for cmd in CI_COMMANDS[name]:
            if cmd not in text:
                errors.append(f"CI command missing: {name}: {cmd}")
    gate = root / "release-check.sh"
    if not gate.is_file():
        errors.append("release-check.sh missing")
    else:
        text = gate.read_text(encoding="utf-8")
        for label, command in LOCAL_COMMANDS.items():
            if command not in text:
                errors.append(f"local gate missing {label}: {command}")
    return errors


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        workflows = root / ".github" / "workflows"
        workflows.mkdir(parents=True)
        gate = root / "release-check.sh"
        gate.write_text("\n".join(LOCAL_COMMANDS.values()))
        for name, steps in STEPS.items():
            (workflows / name).write_text("\n".join(f"      - name: {step}" for step in steps)
                                           + "\n" + "\n".join(CI_COMMANDS[name]))
        for name in CI_ONLY:
            (workflows / name).write_text("# CI-only\n")
        assert not verify(root), verify(root)
        original_gate = gate.read_text()
        gate.write_text(original_gate.replace(LOCAL_COMMANDS["skills"], ""))
        assert any("local gate missing skills" in e for e in verify(root))
        gate.write_text(original_gate)
        path = workflows / "tests.yml"
        original = path.read_text()
        path.write_text(original.replace("      - name: Check skills consistency", ""))
        assert any("CI steps changed" in e for e in verify(root))
        path.write_text(original.replace("bash scripts/check-skills.sh", ""))
        assert any("CI command missing" in e for e in verify(root))
        path.write_text(original)
        (workflows / "surprise.yml").write_text("on: push\n")
        assert any("unregistered workflow" in e for e in verify(root))
    print("PASS: baseline, missing local check, removed CI check/command, new workflow")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        raise SystemExit(self_test())
    if len(sys.argv) != 1:
        raise SystemExit("usage: check-gate-parity.py [--self-test]")
    failures = verify(ROOT)
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        raise SystemExit(1)
    print("PASS: local/PR-CI gate mapping; generation and release declared CI-only")
