"""Architecture observation pipeline — produces visual_architecture_observation.v1 output."""
from __future__ import annotations

import dataclasses
from pathlib import Path

from mq_image_analyze.vision.architecture.classifier import classify_image_type
from mq_image_analyze.vision.architecture.detector import (
    detect_components,
    detect_connections,
    detect_groups,
    infer_dominant_flow,
)
from mq_image_analyze.vision.architecture.observation import (
    SCHEMA_VERSION,
    ArchLayout,
    TextRegion,
    VisualArchitectureObservation,
)


def _try_ocr(image_path: Path) -> tuple[list[TextRegion], bool]:
    """Attempt OCR with pytesseract. Returns (regions, available)."""
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(image_path)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        regions = []
        n = len(data["text"])
        for i in range(n):
            text = data["text"][i].strip()
            conf = int(data["conf"][i])
            if not text or conf < 40:
                continue
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            regions.append(TextRegion(
                text=text,
                bbox=[float(x), float(y), float(x + w), float(y + h)],
                confidence=round(conf / 100.0, 2),
            ))
        return regions, True
    except ImportError:
        return [], False
    except Exception:
        return [], True  # pytesseract present but failed — still mark available


def _image_dimensions(image_path: Path) -> tuple[int, int]:
    try:
        import cv2
        bgr = cv2.imread(str(image_path))
        if bgr is not None:
            h, w = bgr.shape[:2]
            return w, h
    except Exception:
        pass
    try:
        from PIL import Image
        img = Image.open(image_path)
        return img.size
    except Exception:
        return 0, 0


def observe_architecture(image_path: str | Path) -> VisualArchitectureObservation:
    """
    Run the full architecture observation pipeline on an image.
    Returns a VisualArchitectureObservation (schema: visual_architecture_observation.v1).
    """
    path = Path(image_path).expanduser().resolve()

    image_type = classify_image_type(path)
    components = detect_components(path)
    connections = detect_connections(path, components)
    groups = detect_groups(components)
    text_regions, ocr_available = _try_ocr(path)
    dominant_flow = infer_dominant_flow(components)
    img_w, img_h = _image_dimensions(path)

    layout = ArchLayout(
        width=img_w,
        height=img_h,
        component_count=len(components),
        connection_count=len(connections),
        dominant_flow=dominant_flow,
    )

    limitations = _build_limitations(image_type, ocr_available, len(components), len(connections))

    return VisualArchitectureObservation(
        schema_version=SCHEMA_VERSION,
        image_type=image_type,
        image_path=str(path),
        components=components,
        connections=connections,
        groups=groups,
        text_regions=text_regions,
        layout=layout,
        limitations=limitations,
        ocr_available=ocr_available,
    )


def _build_limitations(
    image_type: str,
    ocr_available: bool,
    component_count: int,
    connection_count: int,
) -> list[str]:
    lims = []

    if not ocr_available:
        lims.append(
            "OCR not available — install pytesseract for text extraction from boxes. "
            "Component labels and text fields will be null."
        )
    if image_type == "unknown":
        lims.append(
            "Image type could not be classified. Heuristic component detection may be "
            "inaccurate for this image format."
        )
    if component_count == 0:
        lims.append(
            "No rectangular components detected. The image may use a non-standard "
            "diagram style (rounded shapes, sketch style, or dark-on-dark borders)."
        )
    if connection_count == 0 and component_count > 1:
        lims.append(
            "No connections detected. Arrow/line detection works best on diagrams "
            "with solid thin lines between boxes."
        )
    lims.append(
        "Component and connection detection is heuristic (contour-based). "
        "Overlapping boxes, decorative borders, and complex layouts may produce "
        "false positives or miss real components."
    )
    lims.append(
        "Semantic labels and semantic topology (what each component represents) "
        "are not inferred — this requires an LLM call via mq-mcp review tools."
    )

    return lims
