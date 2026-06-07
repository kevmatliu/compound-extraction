from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.schemas.pipeline_types import CompoundResult


# Job lifecycle states (mirrors the subset of v2's job statuses the frontend expects).
PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"


@dataclass
class JobLogItem:
    id: int
    level: str
    message: str
    created_at: str


@dataclass
class Job:
    id: str
    status: str = PENDING
    logs: list[JobLogItem] = field(default_factory=list)
    summary: Optional[dict] = None
    results: list[CompoundResult] = field(default_factory=list)
    csv_text: Optional[str] = None
    error: Optional[str] = None


class JobStore:
    """In-memory, thread-safe registry of conversion jobs.

    Stateless across restarts by design: jobs (and their CSVs) live only for the
    process lifetime. FastAPI BackgroundTasks run in this same process, so a plain
    dict guarded by a lock is sufficient and avoids any database.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self) -> Job:
        job = Job(id=uuid.uuid4().hex)
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def start(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.status = RUNNING

    def add_log(self, job_id: str, message: str, level: str = "info") -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.logs.append(
                JobLogItem(
                    id=len(job.logs) + 1,
                    level=level,
                    message=message,
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )

    def complete(
        self,
        job_id: str,
        results: list[CompoundResult],
        csv_text: str,
        summary: dict,
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.status = COMPLETED
                job.results = results
                job.csv_text = csv_text
                job.summary = summary

    def fail(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.status = FAILED
                job.error = error
