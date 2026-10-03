"""mq-image analyze <directory>: one record per image, JSONL with --json."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from typer.testing import CliRunner

from mq_image_analyze.cli import app
from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult

runner = CliRunner()


def _result(prompt: str = "p") -> ReversePromptResult:
    return ReversePromptResult(
        objects=["person"], palette=["#000000"], brightness="dark", contrast="high contrast",
        depth="flat", composition="centered", symmetry=0.5, rule_of_thirds=0.2, prompt=prompt,
    )


def _dir(tmp_path: Path) -> Path:
    d = tmp_path / "shots"
    (d / "nested").mkdir(parents=True)
    for name in ("b.png", "a.jpg"):
        Image.new("RGB", (8, 8)).save(d / name)
    Image.new("RGB", (8, 8)).save(d / "nested" / "c.png")
    (d / "notes.txt").write_text("not an image")
    return d


def test_json_is_one_line_per_image_sorted_and_non_recursive(tmp_path: Path):
    d = _dir(tmp_path)
    with patch("mq_image_analyze.cli.analyze.build", return_value=_result()) as build:
        result = runner.invoke(app, ["analyze", str(d), "--json"])
    assert result.exit_code == 0, result.output
    lines = [json.loads(line) for line in result.output.strip().splitlines()]
    assert [Path(r["path"]).name for r in lines] == ["a.jpg", "b.png"]
    assert all(r["prompt"] == "p" for r in lines)
    assert build.call_count == 2


def test_one_failing_image_does_not_stop_the_batch(tmp_path: Path):
    d = _dir(tmp_path)
    with patch(
        "mq_image_analyze.cli.analyze.build",
        side_effect=[RuntimeError("broken file"), _result()],
    ):
        result = runner.invoke(app, ["analyze", str(d), "--json"])
    assert result.exit_code == 1
    lines = [json.loads(line) for line in result.output.strip().splitlines()]
    assert lines[0]["error"] == "broken file"
    assert lines[1]["prompt"] == "p"


def test_text_output_lists_each_image(tmp_path: Path):
    d = _dir(tmp_path)
    with patch("mq_image_analyze.cli.analyze.build", return_value=_result("a short prompt")):
        result = runner.invoke(app, ["analyze", str(d)])
    assert result.exit_code == 0, result.output
    assert "a.jpg" in result.output and "b.png" in result.output
    assert "2 image(s)" in result.output


def test_empty_directory_is_an_error(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    result = runner.invoke(app, ["analyze", str(tmp_path / "empty")])
    assert result.exit_code == 1
    assert "No images" in result.output
