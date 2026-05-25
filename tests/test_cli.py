from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mq_image_analyze.cli import app
from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult

runner = CliRunner()

_MOCK_RESULT = ReversePromptResult(
    objects=["person", "monitor"],
    palette=["#0a0a0f", "#1c1f2e", "#3a4a6b"],
    brightness="dark",
    contrast="moderate contrast",
    depth="shallow depth of field",
    composition="centered",
    symmetry=0.87,
    rule_of_thirds=0.45,
    prompt="person, monitor, dark scene",
)


def test_analyze_help() -> None:
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "IMAGE" in result.output
    assert "--mode" in result.output
    assert "--vision-model" in result.output


def test_analyze_json_output(tmp_path: Path) -> None:
    import numpy as np
    from PIL import Image

    img_path = tmp_path / "test.jpg"
    Image.fromarray(np.zeros((50, 50, 3), dtype="uint8")).save(img_path)

    with patch("mq_image_analyze.cli.analyze.build", return_value=_MOCK_RESULT):
        result = runner.invoke(app, ["analyze", str(img_path), "--json"])

    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert data["brightness"] == "dark"
    assert "objects" in data
    assert "palette" in data
    assert "prompt" in data


def test_analyze_text_output(tmp_path: Path) -> None:
    import numpy as np
    from PIL import Image

    img_path = tmp_path / "test.jpg"
    Image.fromarray(np.zeros((50, 50, 3), dtype="uint8")).save(img_path)

    with patch("mq_image_analyze.cli.analyze.build", return_value=_MOCK_RESULT):
        result = runner.invoke(app, ["analyze", str(img_path)])

    assert result.exit_code == 0
    assert "person" in result.output
    assert "Reverse prompt" in result.output


def test_analyze_passes_vision_backend(tmp_path: Path) -> None:
    import numpy as np
    from PIL import Image

    img_path = tmp_path / "test.jpg"
    Image.fromarray(np.zeros((50, 50, 3), dtype="uint8")).save(img_path)

    with patch("mq_image_analyze.cli.analyze.build", return_value=_MOCK_RESULT) as mock_build:
        result = runner.invoke(
            app,
            [
                "analyze",
                str(img_path),
                "--json",
                "--mode",
                "cloud-verify",
                "--vision-model",
                "gpt-4o",
            ],
        )

    assert result.exit_code == 0
    mock_build.assert_called_once()
    assert mock_build.call_args.kwargs["vision_mode"] == "cloud-verify"
    assert mock_build.call_args.kwargs["vision_model"] == "gpt-4o"


def test_analyze_rejects_unknown_vision_backend(tmp_path: Path) -> None:
    import numpy as np
    from PIL import Image

    img_path = tmp_path / "test.jpg"
    Image.fromarray(np.zeros((50, 50, 3), dtype="uint8")).save(img_path)

    result = runner.invoke(app, ["analyze", str(img_path), "--mode", "not-real"])

    assert result.exit_code == 2
    assert "Unsupported vision mode" in result.output
