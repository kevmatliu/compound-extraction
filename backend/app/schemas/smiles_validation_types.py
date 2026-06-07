from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rdkit import Chem

from app.schemas.enums import ValidationStatus


@dataclass
class SmilesValidationResult:
    status: ValidationStatus
    is_compound: Optional[bool]
    canonical_smiles: Optional[str]
    error: Optional[str]
    mol: Optional[Chem.Mol]
