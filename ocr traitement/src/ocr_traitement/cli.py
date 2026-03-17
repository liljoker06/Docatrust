from __future__ import annotations

import argparse
from pathlib import Path

from .config import Settings
from .detect_fields import draw_detections, detect_invoice_fields_on_image
from .export_csv import build_invoice_row, export_invoice_csv
from .insee_sirene import lookup_sirene
from .io_utils import list_facture_images
from .paddleocr_utils import init_paddleocr, paddle_predict_to_items


def _project_root() -> Path:
    # .../ocr traitement/src/ocr_traitement/cli.py -> .../ocr traitement
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    try:
        import cv2  # type: ignore
    except Exception as e:
        raise SystemExit(
            "OpenCV (cv2) is required for this CLI. Install it with: pip install opencv-python"
        ) from e

    p = argparse.ArgumentParser(prog="ocr-traitement", description="PaddleOCR invoice pipeline (from OCR.ipynb).")
    p.add_argument("--img", type=str, default="", help="Path to a single invoice image to process.")
    p.add_argument("--pattern", type=str, default="clean", help="Filter images in FACTURE_IMG_DIR (default: clean).")
    p.add_argument("--out-csv", type=str, default="outputs/paddleocr_invoice_fields.csv", help="CSV output path.")
    p.add_argument("--annotated", type=str, default="outputs/annotated.jpg", help="Annotated image output path.")
    p.add_argument(
        "--insee",
        action="store_true",
        help="Enrich output using INSEE SIRENE API (requires INSEE_API_KEY_INTEGRATION).",
    )
    p.add_argument(
        "--no-insee",
        action="store_true",
        help="Disable INSEE enrichment even if env var is present.",
    )
    args = p.parse_args(argv)

    root = _project_root()
    settings = Settings.from_env(root)

    if args.img:
        img_path = Path(args.img)
    else:
        imgs = list_facture_images(settings.facture_img_dir, pattern=args.pattern)
        img_path = imgs[0] if imgs else None

    if not img_path or not img_path.exists():
        raise FileNotFoundError(
            f"No image found. Set FACTURE_IMG_DIR env var or place images under {settings.facture_img_dir}"
        )

    paddle_ocr = init_paddleocr(lang="fr")
    img_bgr_full = cv2.imread(str(img_path))
    if img_bgr_full is None:
        raise FileNotFoundError(f"Cannot read image: {img_path}")

    # Downscale before OCR (notebook safety)
    h0, w0 = img_bgr_full.shape[:2]
    max_side = 1280
    scale = min(1.0, max_side / float(max(h0, w0)))
    if scale < 1.0:
        img_bgr = cv2.resize(img_bgr_full, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_AREA)
    else:
        img_bgr = img_bgr_full

    res = paddle_ocr.predict(img_bgr)
    items = paddle_predict_to_items(res)
    dets, _line_items = detect_invoice_fields_on_image(img_bgr, items)

    # Rescale rects back to full image coordinates (for drawing on full-res)
    if scale < 1.0:
        inv = 1.0 / scale
        dets_full = [
            type(d)(
                label=d.label,
                rect=(int(d.rect[0] * inv), int(d.rect[1] * inv), int(d.rect[2] * inv), int(d.rect[3] * inv)),
                text=d.text,
            )
            for d in dets
        ]
    else:
        dets_full = dets

    annotated = draw_detections(img_bgr_full, dets_full)
    out_annot = root / args.annotated
    out_annot.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_annot), annotated)

    row = build_invoice_row(img_path, items, dets)

    # Optional INSEE enrichment
    do_insee: bool
    if args.no_insee:
        do_insee = False
    elif args.insee:
        do_insee = True
    else:
        import os

        do_insee = bool(os.environ.get("INSEE_API_KEY_INTEGRATION") or os.environ.get("INSEE_API_KEY"))

    if do_insee:
        supplier_siret = row.get("supplier_siret", "")
        if supplier_siret:
            insee = lookup_sirene(supplier_siret)
            if insee.ok:
                summary = insee.summary
                # Keep only the most useful legal-unit fields (prefixed)
                keep = [
                    "ul_denomination",
                    "ul_denomination_usuelle",
                    "ul_date_creation",
                    "ul_etat_administratif",
                    "ul_activite_principale",
                    "ul_categorie_juridique",
                    "ul_statut_diffusion",
                ]
                for k in keep:
                    v = summary.get(k)
                    if v not in (None, ""):
                        row[f"insee_{k.removeprefix('ul_')}"] = str(v)
            else:
                row["insee_error"] = (insee.error or "")[:500]
                # Fraud-style alerting:
                # - If SIRET isn't found in INSEE (404), it's a strong anomaly.
                # - If unauthorized/other HTTP, we can't conclude -> mark as not verifiable.
                if insee.http_status == 404:
                    row["fraud_alert"] = "true"
                    row["fraud_reason"] = "SIRET_NOT_FOUND_IN_INSEE"
                elif insee.http_status in (401, 403):
                    row["fraud_alert"] = "unknown"
                    row["fraud_reason"] = "INSEE_UNAUTHORIZED_CANNOT_VERIFY"
                elif insee.http_status:
                    row["fraud_alert"] = "unknown"
                    row["fraud_reason"] = f"INSEE_HTTP_{insee.http_status}"

    out_csv = export_invoice_csv(row, root / args.out_csv)

    print("Image:", img_path)
    print("Annotated:", out_annot)
    print("CSV:", out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

