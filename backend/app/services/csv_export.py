from __future__ import annotations

import csv
import io
from typing import Sequence

from app.schemas.pipeline_types import CSV_COLUMNS, CompoundRow


def rows_to_csv(rows: Sequence[CompoundRow]) -> str:
    """Serialize compound rows to CSV text (header + one line per row)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    for index, row in enumerate(rows):
        writer.writerow(
            [
                index,
                row.source_file,
                row.location,
                row.compound_index,
                row.raw_smiles or "",
                row.canonical_smiles or "",
                row.validation_status,
                row.error or "",
            ]
        )
    return buffer.getvalue()
