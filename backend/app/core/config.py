from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Minimal config for the v3 extract -> SMILES -> CSV pipeline.

    Only what the pipeline needs: where the MolScribe model lives, which device to
    run it on, and a scratch dir. No DB / FAISS / ChemBERTa (those are v2 only).
    """

    model_device: str = Field(default="cpu", alias="MODEL_DEVICE")
    molscribe_model_path: Path = Field(
        default=Path("./models/molscribe/swin_base_char_aux_1m680k.pth"),
        alias="MOLSCRIBE_MODEL_PATH",
    )
    # Scratch dir for transient files. The pipeline uses per-request temp dirs for
    # MolScribe input, so this is just a guaranteed-writable base.
    tmp_dir: Path = Field(default=Path("./tmp"), alias="TMP_DIR")

    api_title: str = "Compound Extraction API"
    api_version: str = "3.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        protected_namespaces=("settings_",),
    )

    def ensure_directories(self) -> None:
        self.tmp_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
