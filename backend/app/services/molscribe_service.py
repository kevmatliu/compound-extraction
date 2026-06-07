from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from app.core.runtime_env import configure_model_runtime_env


def _patch_molscribe_multiprocessing() -> None:
    """Make MolScribe's SMILES post-processing run serially instead of forking a pool.

    MolScribe's ``convert_graph_to_smiles`` spawns ``multiprocessing.Pool(16)`` on
    every prediction to run lightweight RDKit work. On a small CPU box (e.g. a 2-vCPU
    Hugging Face Space) forking 16 children from the ~1GB model process — once per
    image — causes heavy memory thrash and what looks like a hang (minutes per image).
    For our batch sizes (a handful of structures) a serial loop is far faster and
    forks nothing. We rebind the name used inside ``interface.predict_images``.
    """
    import numpy as np
    from molscribe import chemistry, interface

    def serial_convert_graph_to_smiles(coords, symbols, edges, images=None, num_workers=1):
        if images is None:
            results = [
                chemistry._convert_graph_to_smiles(c, s, e)
                for c, s, e in zip(coords, symbols, edges)
            ]
        else:
            results = [
                chemistry._convert_graph_to_smiles(c, s, e, im)
                for c, s, e, im in zip(coords, symbols, edges, images)
            ]
        smiles_list, molblock_list, success = zip(*results)
        return smiles_list, molblock_list, float(np.mean(success))

    interface.convert_graph_to_smiles = serial_convert_graph_to_smiles


class MolScribeService:
    name = "molscribe"

    def __init__(self, model_path: Path, device: str = "cpu") -> None:
        self.model_path = Path(model_path)
        self.device = device
        self._predictor: Optional[Any] = None

    def is_ready(self) -> tuple[bool, str]:
        if not self.model_path.exists():
            return False, f"MolScribe model path does not exist: {self.model_path}"
        try:
            self._load_predictor()
        except Exception as exc:
            return False, str(exc)
        return True, "ready"

    def _load_predictor(self) -> Any:
        if self._predictor is not None:
            return self._predictor

        if not self.model_path.exists():
            raise FileNotFoundError(f"MolScribe model path does not exist: {self.model_path}")

        configure_model_runtime_env()

        try:
            from molscribe import MolScribe
        except Exception as exc:
            raise RuntimeError(f"Failed to import MolScribe: {exc}") from exc

        _patch_molscribe_multiprocessing()
        self._predictor = MolScribe(str(self.model_path), device=self.device)
        return self._predictor

    def image_to_smiles(self, image_path: str) -> str:
        predictor = self._load_predictor()
        source_path = Path(image_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Image path does not exist: {image_path}")

        try:
            prediction = predictor.predict_image_file(str(source_path))
        except TypeError:
            prediction = predictor.predict_image_file(str(source_path), return_confidence=False)

        cleaned = self._normalize_prediction(prediction)
        if not cleaned:
            raise ValueError("MolScribe returned an empty SMILES string")
        return cleaned

    def _normalize_prediction(self, prediction: Any) -> str:
        if isinstance(prediction, str):
            return prediction.strip()
        if isinstance(prediction, tuple) and prediction:
            head = prediction[0]
            if isinstance(head, str):
                return head.strip()
        if isinstance(prediction, list) and prediction:
            head = prediction[0]
            if isinstance(head, str):
                return head.strip()
            if isinstance(head, dict):
                return str(
                    head.get("smiles")
                    or head.get("SMILES")
                    or head.get("prediction")
                    or ""
                ).strip()
        if isinstance(prediction, dict):
            return str(
                prediction.get("smiles")
                or prediction.get("SMILES")
                or prediction.get("prediction")
                or ""
            ).strip()
        return str(prediction or "").strip()
