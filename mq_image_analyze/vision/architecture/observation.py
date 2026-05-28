"""Data classes for visual_architecture_observation.v1 schema."""
from __future__ import annotations

from dataclasses import dataclass, field


SCHEMA_VERSION = "visual_architecture_observation.v1"


@dataclass
class Component:
    id: str
    bbox: list[float]          # [x1, y1, x2, y2] in pixels
    area_percent: float
    label: str | None = None
    fill_color: str | None = None  # dominant hex color inside the box
    text: str | None = None        # OCR result if available


@dataclass
class Connection:
    id: str
    direction: str             # horizontal | vertical | diagonal | unknown
    from_component: str | None = None
    to_component: str | None = None


@dataclass
class Group:
    color: str
    component_ids: list[str] = field(default_factory=list)
    label: str | None = None


@dataclass
class TextRegion:
    text: str
    bbox: list[float]
    confidence: float


@dataclass
class ArchLayout:
    width: int
    height: int
    component_count: int
    connection_count: int
    dominant_flow: str    # left-to-right | top-to-bottom | radial | unknown


@dataclass
class VisualArchitectureObservation:
    schema_version: str
    image_type: str            # architecture-diagram | dashboard | terminal | ui-screenshot | unknown
    image_path: str
    components: list[Component]
    connections: list[Connection]
    groups: list[Group]
    text_regions: list[TextRegion]
    layout: ArchLayout
    limitations: list[str]
    ocr_available: bool
