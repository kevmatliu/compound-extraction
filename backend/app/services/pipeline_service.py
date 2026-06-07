from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable, Optional, Sequence

from app.schemas.enums import ValidationStatus
from app.schemas.pipeline_types import CompoundResult, CompoundRow
from app.services.format_dispatch_service import dispatch_file
from app.services.molscribe_service import MolScribeService
from app.services.smiles_validation import validate_and_standardize_smiles


# Progress sink; defaults to a no-op so the service is usable without a job store.
LogCallback = Callable[[str], None]


def _noop(_: str) -> None:
    return None


class PipelineService:
    """Orchestrates: uploaded file -> candidate crops -> MolScribe -> RDKit -> results.

    Each result pairs a CSV row with the cropped structure image it came from, so
    the UI can show the portion of the source alongside its SMILES. Stateless:
    crops are written to a per-call temp directory only because MolScribe needs a
    file path. One bad candidate or file never aborts the batch — failures become
    error rows so the user still gets a CSV.
    """

    def __init__(self, molscribe: MolScribeService) -> None:
        self.molscribe = molscribe

    def process_files(
        self,
        files: Sequence[tuple[str, bytes]],
        log: Optional[LogCallback] = None,
    ) -> list[CompoundResult]:
        log = log or _noop
        results: list[CompoundResult] = []

        for filename, data in files:
            try:
                candidates = dispatch_file(filename, data)
            except (ValueError, RuntimeError) as exc:
                log(f"{filename}: skipped ({exc})")
                results.append(
                    CompoundResult(
                        row=CompoundRow(
                            source_file=filename,
                            location="-",
                            compound_index=0,
                            raw_smiles=None,
                            canonical_smiles=None,
                            validation_status=ValidationStatus.UNPROCESSED.value,
                            error=str(exc),
                        ),
                        image_png=None,
                    )
                )
                continue

            log(f"{filename}: detected {len(candidates)} candidate structure(s)")
            for index, (image_bytes, location) in enumerate(candidates, start=1):
                results.append(self._process_candidate(filename, location, index, image_bytes))

        return results

    def _process_candidate(
        self,
        filename: str,
        location: str,
        index: int,
        image_bytes: bytes,
    ) -> CompoundResult:
        try:
            raw_smiles = self._recognize(image_bytes)
        except Exception as exc:  # MolScribe / IO failure for this one crop
            return CompoundResult(
                row=CompoundRow(
                    source_file=filename,
                    location=location,
                    compound_index=index,
                    raw_smiles=None,
                    canonical_smiles=None,
                    validation_status=ValidationStatus.PARSE_FAILED.value,
                    error=f"Recognition failed: {exc}",
                ),
                image_png=image_bytes,
            )

        result = validate_and_standardize_smiles(raw_smiles)
        return CompoundResult(
            row=CompoundRow(
                source_file=filename,
                location=location,
                compound_index=index,
                raw_smiles=raw_smiles,
                canonical_smiles=result.canonical_smiles,
                validation_status=result.status.value,
                error=result.error,
            ),
            image_png=image_bytes,
        )

    def _recognize(self, image_bytes: bytes) -> str:
        """Run MolScribe on a crop via a short-lived temp PNG file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.png"
            path.write_bytes(image_bytes)
            return self.molscribe.image_to_smiles(str(path))
