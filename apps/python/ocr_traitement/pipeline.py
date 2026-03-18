from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .extraction.detect_fields import draw_detections, detect_invoice_fields_on_image
from .extraction.export_csv import build_invoice_row
from .insee.insee_sirene import lookup_sirene
from .ocr.paddleocr_utils import init_paddleocr, paddle_predict_to_items
from .validation.validation import alerts_to_json, validate_invoice_row


@dataclass(frozen=True)
class PipelineResult:
    image_path: Path
    row: Dict[str, str]
    annotated_bgr: Any  # numpy array (cv2)


def process_invoice_image(
    image_path: Path,
    *,
    lang: str = "fr",
    max_side: int = 1280,
    enrich_insee: bool = True,
) -> PipelineResult:
    """
    Run OCR + field detection on a single invoice image.

    - Returns `row` compatible with CSV export.
    - Optionally enriches with INSEE fields if env key is present.
    """

    try:
        import cv2  # type: ignore
    except Exception as e:
        raise SystemExit("OpenCV (cv2) is required. Install: pip install opencv-python") from e

    img_bgr_full = cv2.imread(str(image_path))
    if img_bgr_full is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    h0, w0 = img_bgr_full.shape[:2]
    scale = min(1.0, max_side / float(max(h0, w0)))
    if scale < 1.0:
        img_bgr = cv2.resize(img_bgr_full, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_AREA)
    else:
        img_bgr = img_bgr_full

    paddle_ocr = init_paddleocr(lang=lang)
    res = paddle_ocr.predict(img_bgr)
    items = paddle_predict_to_items(res)
    dets, _line_items = detect_invoice_fields_on_image(img_bgr, items)

    # rescale rects for drawing
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
    row = build_invoice_row(image_path, items, dets)

    # INSEE enrichment + fraud alert (same semantics as CLI)
    if enrich_insee:
        import os

        has_key = bool(os.environ.get("INSEE_API_KEY_INTEGRATION") or os.environ.get("INSEE_API_KEY"))
        if has_key:
            supplier_siret = row.get("supplier_siret", "")
            if supplier_siret:
                insee = lookup_sirene(supplier_siret)
                if insee.ok:
                    summary = insee.summary
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
                    if insee.http_status == 404:
                        row["fraud_alert"] = "true"
                        row["fraud_reason"] = "SIRET_NOT_FOUND_IN_INSEE"
                    elif insee.http_status in (401, 403):
                        row["fraud_alert"] = "unknown"
                        row["fraud_reason"] = "INSEE_UNAUTHORIZED_CANNOT_VERIFY"
                    elif insee.http_status:
                        row["fraud_alert"] = "unknown"
                        row["fraud_reason"] = f"INSEE_HTTP_{insee.http_status}"

    alerts = validate_invoice_row(row)
    if alerts:
        row["alerts_count"] = str(len(alerts))
        row["alerts_json"] = alerts_to_json(alerts)
        row["alerts_codes"] = ",".join([a.code for a in alerts])
    else:
        row["alerts_count"] = "0"
        row["alerts_json"] = "[]"
        row["alerts_codes"] = ""

    return PipelineResult(image_path=image_path, row=row, annotated_bgr=annotated)

