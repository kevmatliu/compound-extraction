from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Column order of the exported CSV is exactly the field order below. `id` is the
# result's index in the job, matching the PNG filenames in the ZIP (images/<id>.png).
CSV_COLUMNS = [
    "id",
    "source_file",
    "location",
    "compound_index",
    "raw_smiles",
    "canonical_smiles",
    "validation_status",
    "error",
]


@dataclass
class CompoundRow:
    """One row in the output CSV: a single detected structure (or an error)."""

    source_file: str
    location: str  # e.g. "page 3", "slide 5", "image", or "-" for file-level errors
    compound_index: int  # per-file running index, starting at 1
    raw_smiles: Optional[str]
    canonical_smiles: Optional[str]
    validation_status: str  # ValidationStatus value
    error: Optional[str]


@dataclass
class CompoundResult:
    """A CSV row paired with the cropped structure image it came from.

    The image lets the UI show the portion of the source that produced each SMILES
    (as v2 does in its compound browser). ``image_png`` is None for file-level
    errors (e.g. an unsupported file type) that have no associated crop.
    """

    row: CompoundRow
    image_png: Optional[bytes]
