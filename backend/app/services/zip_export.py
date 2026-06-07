from __future__ import annotations

import io
import zipfile

from app.services.depiction import smiles_to_png
from app.services.job_store import Job


def build_job_zip(job: Job) -> bytes:
    """Package a completed job into a ZIP: the CSV plus per-compound images.

    Layout:
      compounds.csv
      images/<id>.png   clean RDKit depiction of each compound's SMILES
      crops/<id>.png    the original extracted crop the SMILES came from

    <id> is the result's index in the job, matching the CSV `id` column and the
    frontend result id. Entries are skipped when their source is unavailable (no
    renderable SMILES, or no crop), so the ZIP always contains whatever exists.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("compounds.csv", job.csv_text or "")
        for index, result in enumerate(job.results):
            smiles = result.row.canonical_smiles or result.row.raw_smiles
            depiction = smiles_to_png(smiles) if smiles else None
            if depiction is not None:
                archive.writestr(f"images/{index}.png", depiction)
            if result.image_png is not None:
                archive.writestr(f"crops/{index}.png", result.image_png)
    return buffer.getvalue()
