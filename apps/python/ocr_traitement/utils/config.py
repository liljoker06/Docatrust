from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """
    Centralize all paths so scripts are runnable on any machine.

    Defaults assume you generated images via `scripts/generate_facture_images.py`
    and kept outputs under a local folder you choose.
    """

    facture_img_dir: Path

    @staticmethod
    def from_env(project_root: Path) -> "Settings":
        # Prefer env var, else default to a local `facture-images`
        # (we intentionally do NOT hardcode absolute user paths from the notebook).
        import os

        raw = os.environ.get("FACTURE_IMG_DIR")
        if raw:
            return Settings(facture_img_dir=Path(raw).expanduser())

        # Default layout in this repo: `ocr traitement/facture-images/`
        return Settings(facture_img_dir=project_root / "facture-images")

