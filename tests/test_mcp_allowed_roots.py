"""MQ_IMAGE_ALLOWED_ROOTS confines which files the MCP tools may read.

Unset, every readable image is allowed — the behavior before this existed.
Set, a path must resolve inside one of the listed directories, so neither
`..` nor a symlink can lead an agent out of them.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from PIL import Image

from mq_image_analyze.mcp.server import _validate_image


def _image(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8)).save(path)
    return path


def test_unset_allows_any_image(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("MQ_IMAGE_ALLOWED_ROOTS", raising=False)
    img = _image(tmp_path / "a.png")
    assert _validate_image(str(img)) == img.resolve()


def test_inside_a_root_is_allowed(tmp_path: Path, monkeypatch):
    img = _image(tmp_path / "allowed" / "a.png")
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path / "allowed"))
    assert _validate_image(str(img)) == img.resolve()


def test_outside_every_root_is_refused(tmp_path: Path, monkeypatch):
    img = _image(tmp_path / "secret" / "a.png")
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path / "allowed"))
    with pytest.raises(PermissionError, match="MQ_IMAGE_ALLOWED_ROOTS"):
        _validate_image(str(img))


def test_dotdot_cannot_escape(tmp_path: Path, monkeypatch):
    _image(tmp_path / "secret" / "a.png")
    (tmp_path / "allowed").mkdir()
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path / "allowed"))
    with pytest.raises(PermissionError):
        _validate_image(str(tmp_path / "allowed" / ".." / "secret" / "a.png"))


def test_symlink_cannot_escape(tmp_path: Path, monkeypatch):
    target = _image(tmp_path / "secret" / "a.png")
    (tmp_path / "allowed").mkdir()
    link = tmp_path / "allowed" / "link.png"
    link.symlink_to(target)
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path / "allowed"))
    with pytest.raises(PermissionError):
        _validate_image(str(link))


def test_several_roots(tmp_path: Path, monkeypatch):
    img = _image(tmp_path / "two" / "a.png")
    roots = os.pathsep.join([str(tmp_path / "one"), str(tmp_path / "two")])
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", roots)
    assert _validate_image(str(img)) == img.resolve()


def test_a_refused_path_is_not_probed_for_existence(tmp_path: Path, monkeypatch):
    """Outside the roots the answer is the same whether the file exists or not,
    so the error cannot be used to map the disk."""
    monkeypatch.setenv("MQ_IMAGE_ALLOWED_ROOTS", str(tmp_path / "allowed"))
    with pytest.raises(PermissionError):
        _validate_image(str(tmp_path / "nope" / "missing.png"))
