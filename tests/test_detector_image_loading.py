"""Unreadable path-loader input must not become an empty prediction IndexError."""
import pytest
from PIL import Image
from mq_image_analyze.vision.detection import detector


def test_detection_does_not_depend_on_yolo_path_decoder(tmp_path, monkeypatch):
    if not detector._MODEL_PATH.exists():
        pytest.skip('local YOLO weights required')
    from ultralytics.data import loaders
    image = tmp_path / 'valid.png'
    Image.new('RGB', (96, 64), 'white').save(image)
    # This is the path that emits "Image Read Error" in the service log.
    monkeypatch.setattr(loaders, 'imread', lambda *args, **kwargs: None)
    monkeypatch.setattr(detector, '_model', None)
    assert detector.detect(image) == []


def test_unreadable_image_is_reported_before_model_inference(tmp_path, monkeypatch):
    image = tmp_path / 'broken.png'
    image.write_bytes(b'not an image')
    def unexpected_model():
        pytest.fail('invalid image must be rejected before model initialization')
    monkeypatch.setattr(detector, '_get_model', unexpected_model)
    with pytest.raises(ValueError, match='Cannot decode image'):
        detector.detect(image)


def test_empty_model_result_has_explicit_error(tmp_path, monkeypatch):
    image = tmp_path / 'valid.png'
    Image.new('RGB', (16, 16), 'white').save(image)
    monkeypatch.setattr(detector, '_get_model', lambda: lambda *args, **kwargs: [])
    with pytest.raises(RuntimeError, match='returned no prediction'):
        detector.detect(image)
