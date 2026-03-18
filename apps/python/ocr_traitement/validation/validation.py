from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class ValidationAlert:
    code: str
    level: str  # "info" | "warning" | "error"
    message: str
    meta: Dict[str, Any]


def alerts_to_json(alerts: Iterable[ValidationAlert]) -> str:
    return json.dumps([asdict(a) for a in alerts], ensure_ascii=False, separators=(",", ":"))


def _digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


def _parse_amount_fr(s: str) -> Optional[float]:
    """
    Parse French amounts like '1 234,56' or '1234.56' into float.
    Returns None if cannot parse.
    """

    raw = (s or "").strip()
    if not raw:
        return None
    raw = raw.replace("\u00a0", " ").replace(" ", "")
    # Keep digits, separators, minus
    raw = re.sub(r"[^0-9,.\-]", "", raw)
    if not raw or raw in ("-", ".", ","):
        return None

    # If both present, assume comma decimal and dot thousands (or vice-versa)
    if "," in raw and "." in raw:
        # pick last separator as decimal
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    else:
        raw = raw.replace(",", ".")

    try:
        return float(raw)
    except Exception:
        return None


def _parse_date_fr(s: str) -> Optional[date]:
    """
    Parse common French date formats found in OCR: dd/mm/yyyy, dd-mm-yyyy, dd/mm/yy.
    """

    t = (s or "").strip()
    if not t:
        return None
    t = t.replace(".", "/").replace("-", "/")
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", t)
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 100:
        y += 2000
    try:
        return date(y, mo, d)
    except Exception:
        return None


def validate_invoice_row(row: Dict[str, str]) -> List[ValidationAlert]:
    alerts: List[ValidationAlert] = []

    supplier_siret = _digits(row.get("supplier_siret", ""))
    supplier_tva = (row.get("supplier_tva", "") or "").strip().upper().replace(" ", "")

    # --- SIRET basic checks
    if supplier_siret and len(supplier_siret) != 14:
        alerts.append(
            ValidationAlert(
                code="SIRET_FORMAT_INVALID",
                level="error",
                message="Le SIRET fournisseur n'a pas 14 chiffres.",
                meta={"value": row.get("supplier_siret", "")},
            )
        )

    # --- TVA format + coherence with SIREN
    # French VAT: FR + 2 chars (digits/letters) + 9-digit SIREN
    if supplier_tva:
        m = re.match(r"^FR([A-Z0-9]{2})(\d{9})$", supplier_tva)
        if not m:
            alerts.append(
                ValidationAlert(
                    code="VAT_FORMAT_INVALID",
                    level="warning",
                    message="Le numéro de TVA ne correspond pas au format FR.. + SIREN(9).",
                    meta={"value": row.get("supplier_tva", "")},
                )
            )
        else:
            vat_siren = m.group(2)
            if supplier_siret and len(supplier_siret) == 14:
                siret_siren = supplier_siret[:9]
                if vat_siren != siret_siren:
                    alerts.append(
                        ValidationAlert(
                            code="VAT_SIREN_MISMATCH",
                            level="error",
                            message="Incohérence: la TVA (SIREN) ne correspond pas au SIRET.",
                            meta={"vat_siren": vat_siren, "siret_siren": siret_siren},
                        )
                    )

    # --- Totals coherence: TTC ≈ HT + TVA amount
    ht = _parse_amount_fr(row.get("total_ht", ""))
    tva = _parse_amount_fr(row.get("tva", ""))
    ttc = _parse_amount_fr(row.get("total_ttc", ""))
    if ht is not None and tva is not None and ttc is not None:
        expected = ht + tva
        delta = abs(ttc - expected)
        # Tolerance: 0.03€ + 0.2% for OCR noise
        tol = 0.03 + 0.002 * max(1.0, expected)
        if delta > tol:
            alerts.append(
                ValidationAlert(
                    code="TOTALS_INCOHERENT",
                    level="warning",
                    message="Incohérence montants: TTC différent de HT + TVA.",
                    meta={"ht": ht, "tva": tva, "ttc": ttc, "expected_ttc": expected, "delta": delta, "tol": tol},
                )
            )

    # --- Existing INSEE fraud hints (set by pipeline/cli)
    fraud_alert = (row.get("fraud_alert", "") or "").strip().lower()
    fraud_reason = (row.get("fraud_reason", "") or "").strip()
    if fraud_alert == "true" and fraud_reason == "SIRET_NOT_FOUND_IN_INSEE":
        alerts.append(
            ValidationAlert(
                code="SIRET_NOT_FOUND_IN_INSEE",
                level="error",
                message="Aucune entreprise trouvée via INSEE pour ce SIRET (alerte).",
                meta={"supplier_siret": row.get("supplier_siret", ""), "insee_error": row.get("insee_error", "")},
            )
        )
    elif fraud_alert == "unknown" and fraud_reason:
        alerts.append(
            ValidationAlert(
                code="SIRET_CANNOT_BE_VERIFIED_IN_INSEE",
                level="info",
                message="Impossible de vérifier le SIRET via INSEE (clé manquante ou accès refusé).",
                meta={"reason": fraud_reason, "insee_error": row.get("insee_error", "")},
            )
        )

    return alerts


def extract_attestation_vigilance_fields(text: str) -> Dict[str, str]:
    """
    Best-effort extraction for 'attestation de vigilance' OCR text:
    - siret (14 digits)
    - expiry_date (date)
    """

    t = text or ""
    siret = ""
    m_siret = re.search(r"\bSIRET\b[^\d]{0,20}(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})\b", t, re.I)
    if m_siret:
        siret = _digits(m_siret.group(1))
    else:
        # fallback: any 14-digit
        m_any = re.search(r"\b(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})\b", t)
        if m_any:
            siret = _digits(m_any.group(1))

    expiry = ""
    # common wordings: "valable jusqu'au", "jusqu’au", "date de validité", "valable jusqua"
    m_exp = re.search(
        r"(valable\s+jusqu[’']?au|date\s+de\s+validit[ée]|jusqu[’']?au)\s*:?\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
        t,
        re.I,
    )
    if m_exp:
        expiry = m_exp.group(2)
    else:
        # fallback: take first date after 'valable'
        m_exp2 = re.search(r"\bvalable\b[\s\S]{0,40}(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", t, re.I)
        if m_exp2:
            expiry = m_exp2.group(1)

    return {"attestation_siret": siret, "attestation_expiry_date": expiry}


def validate_invoice_vs_attestation(
    invoice_row: Dict[str, str],
    attestation_fields: Dict[str, str],
    *,
    today: Optional[date] = None,
) -> List[ValidationAlert]:
    alerts: List[ValidationAlert] = []
    today = today or datetime.now().date()

    inv_siret = _digits(invoice_row.get("supplier_siret", ""))
    att_siret = _digits(attestation_fields.get("attestation_siret", ""))
    if inv_siret and att_siret and inv_siret != att_siret:
        alerts.append(
            ValidationAlert(
                code="SIRET_MISMATCH_INVOICE_ATTESTATION",
                level="error",
                message="SIRET différent entre facture et attestation de vigilance.",
                meta={"invoice_siret": inv_siret, "attestation_siret": att_siret},
            )
        )

    exp_raw = attestation_fields.get("attestation_expiry_date", "")
    exp = _parse_date_fr(exp_raw)
    if exp is None and exp_raw:
        alerts.append(
            ValidationAlert(
                code="ATTESTATION_EXPIRY_DATE_UNPARSABLE",
                level="warning",
                message="Date de validité/expiration de l'attestation illisible ou non reconnue.",
                meta={"value": exp_raw},
            )
        )
    elif exp is not None and exp < today:
        alerts.append(
            ValidationAlert(
                code="ATTESTATION_EXPIRED",
                level="error",
                message="Attestation de vigilance expirée.",
                meta={"expiry_date": exp.isoformat(), "today": today.isoformat()},
            )
        )

    return alerts

