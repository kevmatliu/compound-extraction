from __future__ import annotations

from enum import Enum


class ValidationStatus(str, Enum):
    """Outcome of parsing/standardizing a SMILES string with RDKit."""

    UNPROCESSED = "unprocessed"
    VALID = "valid"
    PARSE_FAILED = "parse_failed"
    SANITIZE_FAILED = "sanitize_failed"
    STANDARDIZE_FAILED = "standardize_failed"
