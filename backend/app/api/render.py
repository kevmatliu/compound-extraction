from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from app.services.depiction import smiles_to_png

router = APIRouter(prefix="/api")


class RenderRequest(BaseModel):
    smiles: str
    format: str = "png"


@router.post("/render")
def render(request: RenderRequest) -> Response:
    """Render a SMILES string to a PNG. Used as the editor's image-export fallback."""
    png = smiles_to_png(request.smiles)
    if png is None:
        raise HTTPException(status_code=422, detail="Could not render SMILES")
    return Response(content=png, media_type="image/png")
