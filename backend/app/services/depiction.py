from __future__ import annotations

from typing import Optional


def smiles_to_png(smiles: str, size: int = 400) -> Optional[bytes]:
    """Render a SMILES string to a clean 2D structure PNG via RDKit Cairo.

    Returns None on any failure — an unparseable SMILES or a missing Cairo backend —
    so callers (ZIP builder, /api/render) can degrade gracefully rather than error.
    """
    try:
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        drawer = rdMolDraw2D.MolDraw2DCairo(size, size)
        rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
        drawer.FinishDrawing()
        return drawer.GetDrawingText()
    except Exception:
        return None
