from __future__ import annotations

import tomllib
from pathlib import Path


def test_version_file_matches_pyproject() -> None:
    version = Path("VERSION").read_text().strip()
    data = tomllib.loads(Path("pyproject.toml").read_text())

    assert data["project"]["version"] == version


def test_changelog_mentions_current_version() -> None:
    version = Path("VERSION").read_text().strip()

    assert version in Path("CHANGELOG.md").read_text()
