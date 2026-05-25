from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mq_image_analyze.cli import app

runner = CliRunner()


def test_doctor_exits_cleanly() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code in (0, 1)


def test_doctor_json_shape() -> None:
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code in (0, 1)
    data = json.loads(result.output)
    assert "checks" in data
    assert "ok" in data
    assert isinstance(data["checks"], list)
    assert all("check" in c and "ok" in c for c in data["checks"])


def test_doctor_json_has_python_check() -> None:
    result = runner.invoke(app, ["doctor", "--json"])
    data = json.loads(result.output)
    labels = [c["check"] for c in data["checks"]]
    assert "Python >= 3.11" in labels


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "mq-image" in result.output
    assert Path("VERSION").read_text().strip() in result.output
