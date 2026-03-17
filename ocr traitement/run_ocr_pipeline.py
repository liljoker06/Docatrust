from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    """
    Script simple "1 clic" :
    - tu modifies les paths ici
    - tu lances: python3 run_ocr_pipeline.py
    """

    # ==== CONFIG À MODIFIER ICI ====
    FACTURE_IMG_DIR = Path(__file__).resolve().parent / "facture-images"
    IMAGE_FILE: Path | None = None  # ex: FACTURE_IMG_DIR / "facture_2026001_classic_clean.jpg"
    PATTERN = "clean"  # si IMAGE_FILE=None, prend la 1ère image qui match

    OUT_CSV = Path(__file__).resolve().parent / "outputs" / "paddleocr_invoice_fields.csv"
    OUT_ANNOTATED = Path(__file__).resolve().parent / "outputs" / "annotated.jpg"
    # ===============================

    # Permet d'importer `ocr_traitement` sans installer le package
    src_dir = Path(__file__).resolve().parent / "src"
    sys.path.insert(0, str(src_dir))

    try:
        from ocr_traitement.cli import main as cli_main
    except Exception as e:
        raise SystemExit(f"Impossible d'importer le pipeline OCR: {e}") from e

    argv: list[str] = []
    if IMAGE_FILE is not None:
        argv += ["--img", str(IMAGE_FILE)]
    else:
        argv += ["--pattern", PATTERN]

    argv += ["--out-csv", str(OUT_CSV), "--annotated", str(OUT_ANNOTATED)]
    # INSEE enrichment: auto-enabled if INSEE_API_KEY_INTEGRATION is present.

    # Le CLI lit le dossier d'images via Settings.from_env() (env var) :
    # ici on force le chemin depuis le script.
    import os

    os.environ["FACTURE_IMG_DIR"] = str(FACTURE_IMG_DIR)

    return int(cli_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())

