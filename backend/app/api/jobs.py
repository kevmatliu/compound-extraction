from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.dependencies import get_job_store
from app.services.job_store import COMPLETED, JobStore

router = APIRouter(prefix="/api/jobs")


def _result_payload(job_id: str, index: int, result) -> dict:
    """Serialize one CompoundResult for the frontend (image referenced by URL)."""
    row = result.row
    return {
        "id": index,
        "source_file": row.source_file,
        "location": row.location,
        "compound_index": row.compound_index,
        "raw_smiles": row.raw_smiles,
        "canonical_smiles": row.canonical_smiles,
        "validation_status": row.validation_status,
        "error": row.error,
        "image_url": f"/api/jobs/{job_id}/images/{index}" if result.image_png else None,
    }


@router.get("/{job_id}")
def get_job_status(job_id: str, store: JobStore = Depends(get_job_store)) -> dict[str, object]:
    """Return status, streamed logs, summary, and per-compound results for a job."""
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "error": job.error,
        "logs": [asdict(item) for item in job.logs],
        "summary": job.summary,
        "results": [_result_payload(job.id, i, r) for i, r in enumerate(job.results)],
    }


@router.get("/{job_id}/images/{index}")
def get_result_image(job_id: str, index: int, store: JobStore = Depends(get_job_store)) -> Response:
    """Serve the cropped structure PNG for a single result."""
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if index < 0 or index >= len(job.results) or job.results[index].image_png is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=job.results[index].image_png, media_type="image/png")


@router.get("/{job_id}/download")
def download_csv(job_id: str, store: JobStore = Depends(get_job_store)) -> Response:
    """Download the CSV for a completed job."""
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != COMPLETED or job.csv_text is None:
        raise HTTPException(status_code=409, detail=f"Job is not complete (status: {job.status})")
    return Response(
        content=job.csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="compounds.csv"'},
    )
