from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .paddleocr_utils import OcrItem


Rect = Tuple[int, int, int, int]


@dataclass(frozen=True)
class Detection:
    label: str
    rect: Rect
    text: str


def _box_to_rect(box: np.ndarray) -> Rect:
    xs = box[:, 0]
    ys = box[:, 1]
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _rect_center(r: Rect) -> Tuple[float, float]:
    x1, y1, x2, y2 = r
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def _union_rect(rects: Sequence[Rect], pad: int = 6) -> Optional[Rect]:
    if not rects:
        return None
    x1 = min(r[0] for r in rects) - pad
    y1 = min(r[1] for r in rects) - pad
    x2 = max(r[2] for r in rects) + pad
    y2 = max(r[3] for r in rects) + pad
    return max(0, int(x1)), max(0, int(y1)), int(x2), int(y2)


def detect_invoice_fields_on_image(img_bgr: np.ndarray, items: Sequence[OcrItem]) -> Tuple[List[Detection], List[Dict[str, str]]]:
    """
    Port of the notebook 'direct detection' cell.

    Returns:
    - detections: fields + block boxes
    - line_items: parsed table rows (heuristic)
    """

    import re

    h, w = img_bgr.shape[:2]
    amount_rx = re.compile(r"\b\d{1,3}(?:[\s\u00A0]\d{3})*(?:[\,\.]\d{2})\b")

    patterns = {
        "invoice_number": re.compile(r"\bFAC[-\s]*\d{4}[-\s]*\d+\b", re.I),
        "date_emission": re.compile(r"Date\s*d['’]?émission\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.I),
        "date_echeance": re.compile(r"Date\s*d['’]?échéance\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", re.I),
        "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
        "phone": re.compile(r"\b0\d(?:\s\d{2}){4}\b"),
        "siret": re.compile(r"\b\d{3}\s?\d{3}\s?\d{3}\s?\d{5}\b"),
        "iban": re.compile(r"\bFR\d{2}[A-Z0-9\s]{10,}\b", re.I),
        "bic": re.compile(r"\bBIC\b\s*[:\-]?\s*([A-Z0-9]{8,11})\b", re.I),
        "total_ttc": re.compile(r"\bTotal\s*TTC\b", re.I),
        "total_ht": re.compile(r"\bTotal\s*HT\b", re.I),
        "tva": re.compile(r"\bTVA\b", re.I),
    }

    item_rects: List[Tuple[Rect, str, Optional[float]]] = []
    for it in items:
        t = (it.text or "").strip()
        if not t:
            continue
        item_rects.append((_box_to_rect(it.box), t, it.score))

    def _find_anchor(keyword: str) -> Optional[Rect]:
        kw = keyword.upper()
        for r, t, _s in item_rects:
            if kw in t.strip().upper():
                return r
        return None

    r_fourn = _find_anchor("FOURNISSEUR")
    r_client = _find_anchor("CLIENT")
    r_details = _find_anchor("DÉTAILS") or _find_anchor("DETAILS")
    r_totaux = _find_anchor("TOTAUX")
    r_coord = _find_anchor("COORDONN")  # COORDONNEES BANCAIRES

    raw: List[Dict[str, object]] = []
    for r, t, s in item_rects:
        for label, rx in patterns.items():
            if rx.search(t):
                raw.append({"label": label, "rect": r, "text": t, "score": float(s or 0.0)})

    singletons = {
        "invoice_number",
        "date_emission",
        "date_echeance",
        "email",
        "phone",
        "siret",
        "iban",
        "bic",
        "total_ht",
        "tva",
        "total_ttc",
    }

    best: Dict[str, Tuple[Tuple[float, int], Dict[str, object]]] = {}
    dets: List[Detection] = []
    for d in raw:
        label = str(d["label"])
        if label in singletons:
            key = (float(d["score"]), len(str(d["text"])))
            if label not in best or key > best[label][0]:
                best[label] = (key, d)
        else:
            dets.append(Detection(label=label, rect=d["rect"], text=str(d["text"])))

    for _k, d in best.values():
        dets.append(Detection(label=str(d["label"]), rect=d["rect"], text=str(d["text"])))

    def rects_in_band(y_top: int, y_bot: int, x_left: int = 0, x_right: Optional[int] = None) -> List[Rect]:
        if x_right is None:
            x_right = w
        out: List[Rect] = []
        for r, _t, _s in item_rects:
            cx, cy = _rect_center(r)
            if y_top <= cy <= y_bot and x_left <= cx <= x_right:
                out.append(r)
        return out

    # Blocks
    if r_fourn and r_client and r_client[1] > r_fourn[1]:
        sup_rects = rects_in_band(r_fourn[1], r_client[1], 0, int(w * 0.7))
        u = _union_rect(sup_rects)
        if u:
            dets.append(Detection(label="supplier_block", rect=u, text="FOURNISSEUR"))

    if r_client and (r_details or r_totaux):
        y_top = max(0, r_client[1] - 15)
        y_bot = (r_details[1] if r_details else (r_totaux[1] if r_totaux else h))
        if y_bot > y_top:
            stop_kw = ("DÉTAILS", "DETAILS", "PRESTATION", "RÉF", "REF", "DESCRIPTION", "QTE", "QTÉ", "PRIX", "TOTAL")
            cli_rects: List[Rect] = []
            for r, t, _s in item_rects:
                cx, cy = _rect_center(r)
                if not (y_top <= cy <= y_bot and 0 <= cx <= int(w * 0.8)):
                    continue
                tu = t.upper()
                if any(k in tu for k in stop_kw):
                    continue
                cli_rects.append(r)
            u = _union_rect(cli_rects)
            if u:
                dets.append(Detection(label="client_block", rect=u, text="CLIENT"))

    if r_details and r_totaux and r_totaux[1] > r_details[1]:
        tab_rects = rects_in_band(r_details[1], r_totaux[1], 0, w)
        u = _union_rect(tab_rects)
        if u:
            dets.append(Detection(label="table_block", rect=u, text="TABLE"))

    if r_totaux:
        tot_rects = rects_in_band(r_totaux[1], h, int(w * 0.55), w)
        u = _union_rect(tot_rects)
        if u:
            dets.append(Detection(label="totals_block", rect=u, text="TOTAUX"))

    if r_coord:
        bank_rects = rects_in_band(r_coord[1], h, 0, int(w * 0.7))
        u = _union_rect(bank_rects)
        if u:
            dets.append(Detection(label="bank_block", rect=u, text="BANQUE"))

    def _nearest_amount_right(label_rect: Rect) -> Optional[Tuple[int, Rect, str]]:
        lx1, ly1, lx2, ly2 = label_rect
        lcy = (ly1 + ly2) / 2.0
        best_amt: Optional[Tuple[int, Rect, str]] = None
        for r, t, _s in item_rects:
            if r[0] <= lx2:
                continue
            cy = (r[1] + r[3]) / 2.0
            if abs(cy - lcy) > 18:
                continue
            m = amount_rx.search(t.replace("€", ""))
            if not m:
                continue
            dx = r[0] - lx2
            cand = (dx, r, t)
            if best_amt is None or cand[0] < best_amt[0]:
                best_amt = cand
        return best_amt

    total_label_rects: Dict[str, Rect] = {}
    for d in dets:
        if d.label in ("total_ht", "tva", "total_ttc"):
            total_label_rects[d.label] = d.rect

    for key in ("total_ht", "tva", "total_ttc"):
        if key in total_label_rects:
            found = _nearest_amount_right(total_label_rects[key])
            if found:
                _dx, r_amt, t_amt = found
                dets.append(Detection(label=f"{key}_value", rect=r_amt, text=t_amt))

    # Table parsing
    table_rect: Optional[Rect] = next((d.rect for d in dets if d.label == "table_block"), None)
    line_items: List[Dict[str, str]] = []
    if table_rect:
        table_items: List[Tuple[Rect, str]] = []
        for r, t, _s in item_rects:
            cx, cy = _rect_center(r)
            if table_rect[0] <= cx <= table_rect[2] and table_rect[1] <= cy <= table_rect[3]:
                table_items.append((r, t))

        table_items.sort(key=lambda x: (x[0][1], x[0][0]))
        rows: List[List[Tuple[Rect, str]]] = []
        row: List[Tuple[Rect, str]] = []
        last_y: Optional[float] = None
        for r, t in table_items:
            y = r[1]
            if last_y is None or abs(y - last_y) <= 18:
                row.append((r, t))
                last_y = y if last_y is None else (last_y * 0.7 + y * 0.3)
            else:
                rows.append(row)
                row = [(r, t)]
                last_y = y
        if row:
            rows.append(row)

        import re as _re

        ref_rx = _re.compile(r"\b[A-Z]{2,4}[-_]\d{2,4}\b")
        qty_rx = _re.compile(r"\b\d+\b")
        for row in rows:
            joined = " ".join(t for _r, t in row).upper()
            if any(k in joined for k in ["DESIGNATION", "DESCRIPTION", "PRIX", "TOTAL", "QTE", "QTÉ", "RÉF", "REF"]):
                continue
            row = sorted(row, key=lambda x: x[0][0])
            texts = [t for _r, t in row]

            ref = ""
            for t in texts:
                m = ref_rx.search(t.upper())
                if m:
                    ref = m.group(0)
                    break

            amounts: List[Tuple[int, str]] = []
            for r, t in row:
                m = amount_rx.search(t.replace("€", ""))
                if m:
                    amounts.append((r[0], m.group(0)))
            amounts.sort(key=lambda x: x[0])

            qty = ""
            for _r, t in row:
                if qty_rx.fullmatch(t.strip()) and len(t.strip()) <= 3:
                    qty = t.strip()
                    break

            unit_price = ""
            line_total = ""
            if len(amounts) >= 1:
                line_total = amounts[-1][1]
            if len(amounts) >= 2:
                unit_price = amounts[-2][1]

            desc_parts = [
                t
                for t in texts
                if t != ref and t != qty and (unit_price not in t) and (line_total not in t)
            ]
            desc = " ".join(desc_parts).strip()

            if ref or desc or unit_price or line_total:
                line_items.append(
                    {
                        "ref": ref,
                        "description": desc,
                        "qty": qty,
                        "unit_price": unit_price,
                        "line_total": line_total,
                    }
                )

    return dets, line_items


def draw_detections(img_bgr: np.ndarray, detections: Sequence[Detection]) -> np.ndarray:
    import cv2

    out = img_bgr.copy()
    colors = {
        "invoice_number": (0, 200, 0),
        "date_emission": (0, 200, 0),
        "date_echeance": (0, 200, 0),
        "email": (180, 0, 180),
        "phone": (180, 0, 180),
        "siret": (0, 165, 255),
        "iban": (0, 165, 255),
        "bic": (0, 165, 255),
        "total_ht": (0, 0, 255),
        "tva": (0, 0, 255),
        "total_ttc": (0, 0, 255),
        "supplier_block": (0, 255, 255),
        "client_block": (255, 255, 0),
        "table_block": (255, 0, 0),
        "totals_block": (0, 0, 255),
        "bank_block": (0, 165, 255),
    }

    for d in detections:
        x1, y1, x2, y2 = d.rect
        c = colors.get(d.label, (255, 255, 0))
        thick = 4 if d.label.endswith("_block") else 2
        cv2.rectangle(out, (x1, y1), (x2, y2), c, thick)
        cv2.putText(out, d.label, (x1, max(0, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, c, 2)

    return out

