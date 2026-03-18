from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .detect_fields import Detection, Rect
from ..ocr.paddleocr_utils import OcrItem


def _rect_center(r: Rect) -> Tuple[float, float]:
    x1, y1, x2, y2 = r
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def _inside(block: Rect, r: Rect) -> bool:
    x, y = _rect_center(r)
    x1, y1, x2, y2 = block
    return x1 <= x <= x2 and y1 <= y <= y2


def _box_to_rect(box) -> Rect:
    import numpy as np

    b = np.array(box)
    return (int(b[:, 0].min()), int(b[:, 1].min()), int(b[:, 0].max()), int(b[:, 1].max()))


def _first_match(rx: str, text: str) -> str:
    import re

    m = re.search(rx, text or "", re.I)
    return m.group(1).strip() if m else ""


def _parse_party(block_text: str, keyword: str) -> Tuple[str, str, str]:
    import re

    lines = [l.strip() for l in (block_text or "").split("\n") if l.strip()]
    lines = [l for l in lines if l.upper() != keyword]

    drop = (
        "DÉTAILS",
        "DETAILS",
        "PRESTATIONS",
        "PRESTATION",
        "RÉF",
        "REF",
        "DESCRIPTION",
        "QTÉ",
        "QTE",
        "PRIX",
        "TOTAL",
    )
    lines = [l for l in lines if not any(k in l.upper() for k in drop)]

    name = lines[0] if len(lines) >= 1 else ""
    address = lines[1] if len(lines) >= 2 else ""

    city = ""
    for l in lines[2:6]:
        if re.search(r"\b\d{5}\b", l):
            city = l
            break
    if not city:
        city = lines[2] if len(lines) >= 3 else ""

    return name, address, city


def build_invoice_row(
    image_file: Optional[Path],
    items: Sequence[OcrItem],
    dets: Sequence[Detection],
) -> Dict[str, str]:
    import re

    blocks = {d.label: d.rect for d in dets if d.label.endswith("_block")}

    def text_in_block(block_label: str) -> str:
        rect = blocks.get(block_label)
        if not rect:
            return ""
        rows: List[Tuple[int, int, str]] = []
        for it in items:
            t = (it.text or "").strip()
            if not t:
                continue
            r = _box_to_rect(it.box)
            if _inside(rect, r):
                rows.append((r[1], r[0], t))
        rows.sort()
        return "\n".join([t for _, _, t in rows])

    supplier_text = text_in_block("supplier_block")
    client_text = text_in_block("client_block")
    totals_text = text_in_block("totals_block")
    bank_text = text_in_block("bank_block")

    field_map: Dict[str, str] = {}
    for d in dets:
        if d.label.endswith("_block"):
            continue
        field_map[d.label] = d.text

    supplier_name, supplier_address, supplier_city = _parse_party(supplier_text, "FOURNISSEUR")
    client_name, client_address, client_city = _parse_party(client_text, "CLIENT")

    total_ht = _first_match(r"Total\s*HT\s*:?\s*([\d\s.,]+)\s*€?", totals_text)
    tva_amt = _first_match(r"TVA\s*:?\s*([\d\s.,]+)\s*€?", totals_text)
    total_ttc = _first_match(r"Total\s*TTC\s*:?\s*([\d\s.,]+)\s*€?", totals_text)

    if not total_ht:
        total_ht = _first_match(r"Total\s*HT\s*:?\s*([\d\s.,]+)", field_map.get("total_ht_value", field_map.get("total_ht", "")))
    if not tva_amt:
        tva_amt = _first_match(r"TVA\s*:?\s*([\d\s.,]+)", field_map.get("tva_value", field_map.get("tva", "")))
    if not total_ttc:
        total_ttc = _first_match(r"Total\s*TTC\s*:?\s*([\d\s.,]+)", field_map.get("total_ttc_value", field_map.get("total_ttc", "")))

    iban = _first_match(r"\bIBAN\b\s*:?\s*([A-Z0-9\s]{10,})", bank_text)
    bic = _first_match(r"\bBIC\b\s*:?\s*([A-Z0-9]{8,11})", bank_text)

    invoice_number = _first_match(r"(FAC[-\s]*\d{4}[-\s]*\d+)", field_map.get("invoice_number", ""))
    date_emission = _first_match(r"(\d{1,2}/\d{1,2}/\d{2,4})", field_map.get("date_emission", ""))
    date_echeance = _first_match(r"(\d{1,2}/\d{1,2}/\d{2,4})", field_map.get("date_echeance", ""))

    phone = _first_match(r"(0\d(?:\s\d{2}){4})", field_map.get("phone", ""))
    email = _first_match(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", field_map.get("email", ""))
    siret = _first_match(r"(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})", field_map.get("siret", ""))
    tva_id = field_map.get("tva", "")

    return {
        "image_file": str(image_file) if image_file else "",
        "invoice_number": invoice_number,
        "date_emission": date_emission,
        "date_echeance": date_echeance,
        "supplier_name": supplier_name,
        "supplier_address": supplier_address,
        "supplier_city": supplier_city,
        "supplier_phone": phone,
        "supplier_email": email,
        "supplier_siret": re.sub(r"\s+", "", siret),
        "supplier_tva": tva_id,
        "client_name": client_name,
        "client_address": client_address,
        "client_city": client_city,
        "total_ht": total_ht,
        "tva": tva_amt,
        "total_ttc": total_ttc,
        "bic": bic,
        "iban": re.sub(r"\s+", " ", iban).strip(),
        "raw_supplier_block": supplier_text,
        "raw_client_block": client_text,
        "raw_totals_block": totals_text,
    }


def export_invoice_csv(row: Dict[str, str], out_csv: Path) -> Path:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    # Avoid pandas dependency (can break on some local Python installs due to binary wheels).
    import csv

    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()), delimiter=";")
        writer.writeheader()
        writer.writerow(row)
    return out_csv

