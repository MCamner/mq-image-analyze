"""Redaction before an image leaves the machine for cloud-verify.

Opt-in (`redact=True` or MQ_IMAGE_REDACT_CLOUD=1) and fail-closed: when
redaction is asked for but OCR cannot run, the image is not sent at all.
OCR is replaced by a fixture here, so the tests do not need tesseract.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from mq_image_analyze.vision import redaction


def _image(tmp_path: Path) -> Path:
    path = tmp_path / "shot.png"
    Image.new("RGB", (200, 100), color=(255, 255, 255)).save(path)
    return path


def _words(*items):
    """(text, bbox, line) tuples as _ocr_words returns them."""
    return list(items)


@pytest.mark.parametrize(
    "text",
    ["19800101-1234", "800101-1234", "198001011234", "8001011234", "800101+1234", "anna.berg@region.se"],
)
def test_sensitive_tokens_are_masked(tmp_path: Path, text: str):
    words = _words((text, (10, 10, 90, 30), 1))
    with patch.object(redaction, "_ocr_words", return_value=words):
        result = redaction.redact_for_cloud(_image(tmp_path), tmp_path)
    assert result.path is not None
    assert result.redacted == 1
    with Image.open(result.path) as img:
        assert img.getpixel((50, 20)) == (0, 0, 0)
        assert img.getpixel((150, 80)) == (255, 255, 255)


def test_a_personnummer_split_in_two_tokens_is_masked(tmp_path: Path):
    words = _words(("800101", (10, 10, 50, 30), 1), ("1234", (55, 10, 90, 30), 1))
    with patch.object(redaction, "_ocr_words", return_value=words):
        result = redaction.redact_for_cloud(_image(tmp_path), tmp_path)
    assert result.redacted == 2


def test_tokens_on_different_lines_are_not_joined(tmp_path: Path):
    words = _words(("800101", (10, 10, 50, 30), 1), ("1234", (10, 50, 50, 70), 2))
    with patch.object(redaction, "_ocr_words", return_value=words):
        result = redaction.redact_for_cloud(_image(tmp_path), tmp_path)
    assert result.redacted == 0


def test_ordinary_text_is_left_alone(tmp_path: Path):
    words = _words(("Release", (10, 10, 60, 30), 1), ("2026-10-03", (70, 10, 140, 30), 1))
    with patch.object(redaction, "_ocr_words", return_value=words):
        result = redaction.redact_for_cloud(_image(tmp_path), tmp_path)
    assert result.redacted == 0
    assert result.path is not None


def test_no_ocr_means_not_sent(tmp_path: Path):
    with patch.object(redaction, "_ocr_words", side_effect=redaction.OcrUnavailable("no tesseract")):
        result = redaction.redact_for_cloud(_image(tmp_path), tmp_path)
    assert result.path is None
    assert any("not sent" in note for note in result.notes)


# ── wiring into build ────────────────────────────────────────────────────────

def _build(tmp_path: Path, **kwargs):
    from mq_image_analyze.reasoning.prompts.reverse_prompt import build
    return build(_image(tmp_path), **kwargs)


def test_build_sends_the_redacted_copy(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("MQ_IMAGE_REDACT_CLOUD", raising=False)
    words = _words(("anna@x.se", (10, 10, 90, 30), 1))
    with patch.object(redaction, "_ocr_words", return_value=words), patch(
        "mq_image_analyze.reasoning.prompts.reverse_prompt.semantic_describe",
        return_value=("caption", "cloud-verify", "gpt-4.1"),
    ) as describe:
        result = _build(tmp_path, vision_mode="cloud-verify", redact=True)
    sent = Path(describe.call_args.args[0])
    assert sent.name != "shot.png"
    assert result.semantic_caption == "caption"
    assert any("1 region" in item for item in result.limitations)


def test_build_does_not_send_when_ocr_is_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MQ_IMAGE_REDACT_CLOUD", "1")
    with patch.object(redaction, "_ocr_words", side_effect=redaction.OcrUnavailable("x")), patch(
        "mq_image_analyze.reasoning.prompts.reverse_prompt.semantic_describe"
    ) as describe:
        result = _build(tmp_path, vision_mode="cloud-verify")
    describe.assert_not_called()
    assert result.semantic_caption is None
    assert result.vision_mode == "cloud-verify"
    assert any("not sent" in item for item in result.limitations)


def test_local_modes_are_never_redacted(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("MQ_IMAGE_REDACT_CLOUD", "1")
    with patch.object(redaction, "redact_for_cloud") as redact, patch(
        "mq_image_analyze.reasoning.prompts.reverse_prompt.semantic_describe",
        return_value=(None, "local-fast", "bakllava"),
    ):
        _build(tmp_path, vision_mode="local-fast")
    redact.assert_not_called()


def test_cli_analyze_passes_redact(tmp_path: Path):
    from typer.testing import CliRunner

    from mq_image_analyze.cli import app
    from mq_image_analyze.reasoning.prompts.reverse_prompt import ReversePromptResult

    fake = ReversePromptResult(
        objects=[], palette=[], brightness="", contrast="", depth="", composition="",
        symmetry=0.0, rule_of_thirds=0.0, prompt="p",
    )
    with patch("mq_image_analyze.cli.analyze.build", return_value=fake) as build:
        result = CliRunner().invoke(
            app, ["analyze", str(_image(tmp_path)), "--mode", "cloud-verify", "--redact", "--json"]
        )
    assert result.exit_code == 0, result.output
    assert build.call_args.kwargs["redact"] is True


def test_mcp_tools_pass_redact(tmp_path: Path):
    from mq_image_analyze.mcp import server

    img = str(_image(tmp_path))
    with patch("mq_image_analyze.reasoning.prompts.reverse_prompt.build") as build:
        build.return_value = __import__(
            "mq_image_analyze.reasoning.prompts.reverse_prompt", fromlist=["ReversePromptResult"]
        ).ReversePromptResult(
            objects=[], palette=[], brightness="", contrast="", depth="", composition="",
            symmetry=0.0, rule_of_thirds=0.0, prompt="p",
        )
        server.analyze_image(img, vision_mode="cloud-verify", redact=True)
        assert build.call_args.kwargs["redact"] is True
        server.reverse_prompt(img, vision_mode="cloud-verify", redact=True)
        assert build.call_args.kwargs["redact"] is True
