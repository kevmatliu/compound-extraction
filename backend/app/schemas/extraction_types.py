from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ExtractionTuning:
    raster_dpi: int = 300
    render_scale: float = 300.0 / 72.0
    binary_threshold: int = 220
    dilation_kernel_size: int = 4
    dilation_kernel_size_large: int = 20
    dilation_large_iterations: int = 2
    min_width: int = 120
    min_height: int = 120
    max_page_fraction: float = 0.85
    padding: int = 20
    density_min: float = 0.02
    density_max: float = 0.15
    complexity_bins: int = 80
    complexity_smooth_sigma: float = 2.0
    aspect_ratio_max: float = 6.0
    min_line_length: int = 15
    max_line_gap: int = 4
    hough_threshold: int = 20
    angle_tolerance_degrees: float = 8.0
    angle_alignment_min: float = 0.55
    angle_alignment_ring_override: float = 0.45
    border_endpoint_zone_ratio: float = 0.15
    border_endpoint_ratio_bonus_min: float = 0.15
    letter_width_min: int = 6
    letter_width_max: int = 22
    letter_aspect_ratio_min: float = 1.3
    letter_aspect_ratio_max: float = 4.0
    letter_component_ratio_max: float = 0.60
    nms_iou_threshold: float = 0.30
    nested_overlap_threshold: float = 0.60
    expansion_ratio: float = 0.08
    expansion_min_pixels: int = 20


@dataclass
class CompoundOccurrence:
    compound_number: Optional[str]
    page: int
    image_bytes: bytes
    bbox: tuple[int, int, int, int]
    assay_data: dict[str, Any] = field(default_factory=dict)
    smiles_data: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompoundPatent:
    patent_id: str
    compounds: list[CompoundOccurrence] = field(default_factory=list)

    def add_compound(self, compound: CompoundOccurrence) -> None:
        self.compounds.append(compound)

    def get_compounds(self) -> list[CompoundOccurrence]:
        return self.compounds


@dataclass
class CandidateBox:
    bbox: tuple[int, int, int, int]
    density: float
    angle_alignment_score: float
    ring_count: int
    border_endpoint_ratio: float
    convex_hull_fill_ratio: float
    letter_component_ratio: float
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
