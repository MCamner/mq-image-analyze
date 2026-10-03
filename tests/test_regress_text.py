"""regress reads the text in changed regions: what changed, not only where.

OCR runs once per image on changed screens; each changed region collects the
whole words that overlap it, so a change to the last letter still reads as
the full word. Stubbed OCR keeps these tests independent of tesseract; the
last test uses the real engine and is skipped when it is not installed.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image, ImageDraw
from typer.testing import CliRunner

from mq_image_analyze import perception
from mq_image_analyze.cli import app
from mq_image_analyze.pipelines.ocr_pipeline import OcrUnavailable
from mq_image_analyze.reasoning.comparison import text_diff
from mq_image_analyze.reasoning.comparison.regress import regress

runner = CliRunner()
OCR = "mq_image_analyze.reasoning.comparison.text_diff.ocr_words"
TEXT = "mq_image_analyze.reasoning.comparison.text_diff.text_changes"


def _change(before: str, after: str) -> list[dict]:
    return [{"bbox": [18, 18, 72, 42], "kind": text_diff.classify(before, after), "before": before, "after": after}]


def _pair(tmp_path: Path) -> tuple[Path, Path]:
    base, cur = tmp_path / "b", tmp_path / "c"
    for d, fill in ((base, "black"), (cur, (110, 110, 110))):
        d.mkdir()
        img = Image.new("RGB", (200, 100), "white")
        ImageDraw.Draw(img).rectangle((20, 20, 70, 40), fill=fill)
        img.save(d / "s.png")
    return base, cur


def _words(*items):
    return [(text, box, line) for text, box, line in items]


REGION = {"bbox": [18, 18, 72, 42], "area_percent": 6.0}


@pytest.mark.parametrize(
    "before, after, kind",
    [
        ("Logga in", "Fortsätt", "changed"),
        ("", "Ny", "added"),
        ("Gammal", "", "removed"),
        ("Spara", "Spara", "visual"),
        ("", "", "visual"),
    ],
)
def test_kinds(before, after, kind):
    assert text_diff.classify(before, after) == kind


def test_the_read_box_grows_to_whole_words():
    """A change to the last letters must still read the full word."""
    words = _words(("Logga", (20, 20, 45, 40), 1), ("Rubrik", (100, 70, 150, 90), 2))
    box = text_diff.read_box([40, 22, 46, 38], words, [], (200, 100))
    assert box[0] <= 20 and box[2] >= 45
    assert box[2] < 100, "a word that does not overlap the region is not pulled in"


def test_regress_attaches_text_changes(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, return_value=_change("Logga", "Fortsätt")):
        entry = regress(base, cur, fail_over=0.0).entries[0]
    assert entry.text_ocr == "available"
    assert entry.text_changes[0]["kind"] == "changed"


def test_regress_without_ocr_says_so(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, side_effect=OcrUnavailable("no tesseract")):
        entry = regress(base, cur, fail_over=0.0).entries[0]
    assert entry.text_ocr == "unavailable"
    assert entry.text_changes == []
    assert entry.status == "changed" and entry.failed


def test_text_false_skips_ocr(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT) as ocr:
        entry = regress(base, cur, fail_over=0.0, text=False).entries[0]
    ocr.assert_not_called()
    assert entry.text_ocr is None


# ── --fail-on text ───────────────────────────────────────────────────────────

def test_fail_on_text_passes_a_visual_only_change(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, return_value=_change("Spara", "Spara")):
        entry = regress(base, cur, fail_over=0.0, fail_on="text").entries[0]
    assert entry.status == "changed"
    assert not entry.failed


def test_fail_on_text_fails_a_text_change(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, return_value=_change("A", "B")):
        entry = regress(base, cur, fail_over=0.0, fail_on="text").entries[0]
    assert entry.failed


def test_fail_on_text_without_ocr_fails_closed(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, side_effect=OcrUnavailable("x")):
        entry = regress(base, cur, fail_over=0.0, fail_on="text").entries[0]
    assert entry.failed


# ── perception record ────────────────────────────────────────────────────────

def test_text_changes_become_quoted_risk_signals_with_a_data_warning(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, return_value=_change("Logga", "Fortsätt")):
        entry = regress(base, cur, fail_over=0.0).entries[0]
    record = perception.from_regression(entry, fail_over=0.0, source_type="screenshot")
    assert any('"Logga" → "Fortsätt"' in s for s in record["risk_signals"])
    assert "Fortsätt" in record["ocr_text"]
    assert any("must not be executed" in item for item in record["limitations"])


def test_long_ocr_text_is_truncated_in_signals():
    entry_text = "x" * 500
    signal = perception._quote(entry_text)
    assert len(signal) < 100 and signal.endswith('…"')


# ── CLI ──────────────────────────────────────────────────────────────────────

def test_cli_fail_on_text_and_no_text(tmp_path: Path):
    base, cur = _pair(tmp_path)
    with patch(TEXT, return_value=_change("Spara", "Spara")):
        result = runner.invoke(app, ["regress", str(base), str(cur), "--fail-on", "text", "--json"])
    assert result.exit_code == 0, result.output
    line = json.loads(result.stdout.strip())
    assert line["text_changes"][0]["kind"] == "visual"

    with patch(TEXT) as ocr:
        result = runner.invoke(app, ["regress", str(base), str(cur), "--no-text"])
    ocr.assert_not_called()
    assert result.exit_code == 1


def test_cli_rejects_unknown_fail_on(tmp_path: Path):
    base, cur = _pair(tmp_path)
    assert runner.invoke(app, ["regress", str(base), str(cur), "--fail-on", "pixels"]).exit_code == 2


# ── real OCR ─────────────────────────────────────────────────────────────────

@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")
def test_real_ocr_reads_a_relabeled_button(tmp_path: Path):
    pytest.importorskip("pytesseract")
    from PIL import ImageFont

    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    if not Path(font_path).is_file():
        pytest.skip("Arial not available")
    font = ImageFont.truetype(font_path, 28)
    base, cur = tmp_path / "b", tmp_path / "c"
    for d, label in ((base, "Logga in"), (cur, "Fortsätt")):
        d.mkdir()
        img = Image.new("RGB", (480, 160), "white")
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "Användarnamn", fill="black", font=font)
        draw.text((20, 90), label, fill="black", font=font)
        img.save(d / "login.png")
        button = Image.new("RGB", (480, 160), "white")
        bdraw = ImageDraw.Draw(button)
        bdraw.rectangle((20, 60, 220, 110), fill=(40, 110, 200))
        bdraw.text((36, 68), label, fill="white", font=font)
        button.save(d / "button.png")
    entries = {e.name: e for e in regress(base, cur, fail_over=0.0).entries}
    for name in ("login.png", "button.png"):
        assert entries[name].text_ocr == "available", name
        changed = [c for c in entries[name].text_changes if c["kind"] == "changed"]
        assert changed, f"{name}: {entries[name].text_changes}"
        assert changed[0]["before"] == "Logga in", name
        assert changed[0]["after"] in ("Fortsätt", "Fortsatt"), name
    entry = entries["login.png"]
    changed = [c for c in entry.text_changes if c["kind"] == "changed"]
    assert changed and changed[0]["before"] == "Logga in"
    # "Fortsätt" with the swe language pack, "Fortsatt" with English only.
    assert changed[0]["after"] in ("Fortsätt", "Fortsatt")


def test_ocr_lang_prefers_swedish_when_installed(monkeypatch):
    pytest.importorskip("pytesseract")
    from mq_image_analyze.pipelines import ocr_pipeline

    monkeypatch.delenv("MQ_IMAGE_OCR_LANG", raising=False)
    with patch("pytesseract.get_languages", return_value=["eng", "osd", "swe"]):
        assert ocr_pipeline.ocr_lang() == "swe+eng"
    with patch("pytesseract.get_languages", return_value=["eng", "osd"]):
        assert ocr_pipeline.ocr_lang() == "eng"
    monkeypatch.setenv("MQ_IMAGE_OCR_LANG", "deu")
    assert ocr_pipeline.ocr_lang() == "deu"
