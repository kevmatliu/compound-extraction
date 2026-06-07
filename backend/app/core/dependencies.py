from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.services.job_store import JobStore
from app.services.molscribe_service import MolScribeService
from app.services.pipeline_service import PipelineService


@lru_cache(maxsize=1)
def get_molscribe_service() -> MolScribeService:
    settings = get_settings()
    return MolScribeService(model_path=settings.molscribe_model_path, device=settings.model_device)


@lru_cache(maxsize=1)
def get_pipeline_service() -> PipelineService:
    return PipelineService(get_molscribe_service())


@lru_cache(maxsize=1)
def get_job_store() -> JobStore:
    return JobStore()
