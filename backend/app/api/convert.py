from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.core.dependencies import get_job_store, get_pipeline_service
from app.services.csv_export import rows_to_csv
from app.services.job_store import JobStore
from app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/api")


def _run_convert_job(
    job_id: str,
    payloads: list[tuple[str, bytes]],
    pipeline: PipelineService,
    store: JobStore,
) -> None:
    """Background worker: run the pipeline and store the resulting CSV on the job."""
    store.start(job_id)
    store.add_log(job_id, f"Starting conversion of {len(payloads)} file(s).")
    try:
        results = pipeline.process_files(payloads, log=lambda msg: store.add_log(job_id, msg))
        rows = [r.row for r in results]
        csv_text = rows_to_csv(rows)
        valid = sum(1 for r in rows if r.validation_status == "valid")
        summary = {
            "files": len(payloads),
            "total_rows": len(rows),
            "valid_compounds": valid,
        }
        store.add_log(job_id, f"Done. {valid}/{len(rows)} rows produced valid SMILES.")
        store.complete(job_id, results, csv_text, summary)
    except Exception as exc:  # safety net; per-item errors are already row-level
        store.add_log(job_id, f"Job failed: {exc}", level="error")
        store.fail(job_id, str(exc))


@router.post("/convert")
async def convert(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    pipeline: PipelineService = Depends(get_pipeline_service),
    store: JobStore = Depends(get_job_store),
) -> dict[str, str]:
    """Accept uploaded files and kick off a background conversion job.

    Returns a job id the client polls via /api/jobs/{id}; the CSV is downloaded
    from /api/jobs/{id}/download once the job is complete.
    """
    payloads: list[tuple[str, bytes]] = []
    for index, upload in enumerate(files, start=1):
        data = await upload.read()
        if not data:
            continue
        payloads.append((upload.filename or f"upload-{index}", data))

    if not payloads:
        raise HTTPException(status_code=400, detail="No non-empty files were uploaded.")

    job = store.create()
    background_tasks.add_task(_run_convert_job, job.id, payloads, pipeline, store)
    return {"job_id": job.id, "status": job.status}
