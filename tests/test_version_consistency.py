from __future__ import annotations

import tomllib
from pathlib import Path
from unittest.mock import patch

from mq_image_analyze import cli


def test_version_file_matches_pyproject() -> None:
    version = Path("VERSION").read_text().strip()
    data = tomllib.loads(Path("pyproject.toml").read_text())

    assert data["project"]["version"] == version


def test_changelog_mentions_current_version() -> None:
    version = Path("VERSION").read_text().strip()

    assert version in Path("CHANGELOG.md").read_text()


def test_cli_version_uses_package_metadata_when_version_file_is_absent() -> None:
    with (
        patch("mq_image_analyze.cli.version", return_value="1.3.0"),
        patch("pathlib.Path.exists", return_value=False),
        patch("pathlib.Path.read_text", side_effect=AssertionError("VERSION file should not be read")),
    ):
        assert cli._read_version() == "1.3.0"
