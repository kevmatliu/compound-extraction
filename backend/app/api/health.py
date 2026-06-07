from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_molscribe_service
from app.services.molscribe_service import MolScribeService

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check(
    molscribe: MolScribeService = Depends(get_molscribe_service),
) -> dict[str, object]:
    """Report service liveness and whether the MolScribe model is loadable."""
    ready, message = molscribe.is_ready()
    return {"status": "ok", "molscribe_ready": ready, "molscribe_detail": message}
