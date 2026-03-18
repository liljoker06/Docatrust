from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _ensure_imports():
    # Run without installing the package: add src/ to path
    import sys

    sys.path.insert(0, str(_project_root() / "src"))

    from ocr_traitement.insee_sirene import lookup_sirene  # noqa: F401
    from ocr_traitement.pipeline import process_invoice_image  # noqa: F401
    from ocr_traitement.validation import validate_invoice_row  # noqa: F401


_ensure_imports()

from ocr_traitement.insee_sirene import lookup_sirene
from ocr_traitement.pipeline import process_invoice_image
from ocr_traitement.paddleocr_utils import init_paddleocr, paddle_predict_to_items
from ocr_traitement.validation import (
    ValidationAlert,
    alerts_to_json,
    extract_attestation_vigilance_fields,
    validate_invoice_row,
    validate_invoice_vs_attestation,
)


st.set_page_config(page_title="Docatrust OCR", page_icon="🧾", layout="wide")

st.markdown("## Docatrust — OCR + Vérifications (INSEE)")

with st.sidebar:
    st.markdown("### Configuration")
    st.code(f"INSEE_API_KEY_INTEGRATION={'SET' if os.environ.get('INSEE_API_KEY_INTEGRATION') else 'NOT SET'}")
    base = os.environ.get("INSEE_SIRENE_BASE_URL", "https://api.insee.fr/api-sirene/3.11")
    st.text_input("INSEE_SIRENE_BASE_URL (env)", value=base, disabled=True)
    st.caption("Charge ton `.env` avant de lancer Streamlit (ou exporte les variables).")

    st.markdown("### Validation")
    st.caption("Optionnel: ajoute une attestation pour comparer le SIRET et la date de validité.")

tab_upload, tab_sirene = st.tabs(["Upload facture (OCR)", "Recherche Sirene (INSEE)"])


@st.cache_resource
def _get_paddle(lang: str = "fr"):
    return init_paddleocr(lang=lang)


def _alerts_to_rows(alerts: List[ValidationAlert]) -> List[Dict[str, Any]]:
    return [{"level": a.level, "code": a.code, "message": a.message, **(a.meta or {})} for a in alerts]


def _tmp_write(uploaded) -> Path:
    suffix = Path(uploaded.name).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded.getvalue())
        return Path(f.name)


def _digits(s: str) -> str:
    import re

    return re.sub(r"\D+", "", s or "")


with tab_upload:
    st.markdown("### Upload d’une facture (image)")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        uploaded = st.file_uploader("Image facture (jpg/png/webp)", type=["jpg", "jpeg", "png", "webp"])
        uploaded_att = st.file_uploader(
            "Attestation de vigilance (optionnel) (jpg/png/webp)",
            type=["jpg", "jpeg", "png", "webp"],
            key="attestation",
        )
        run = st.button("Lancer le traitement", type="primary", disabled=(uploaded is None))

        if uploaded is not None:
            st.image(uploaded, caption="Facture uploadée", use_container_width=True)
        if uploaded_att is not None:
            st.image(uploaded_att, caption="Attestation uploadée", use_container_width=True)

    with col2:
        if run and uploaded is not None:
            try:
                tmp_path = _tmp_write(uploaded)
                res = process_invoice_image(tmp_path, enrich_insee=True)

                st.markdown("### Résultat")
                st.markdown("#### Champs (CSV row)")
                row: Dict[str, Any] = dict(res.row)

                # Show fraud alert if any
                fraud = row.get("fraud_alert")
                if fraud in ("true", "unknown"):
                    st.warning(f"Fraud alert: {fraud} — {row.get('fraud_reason','')}")

                # Intelligent alerts (invoice + optional attestation)
                alerts: List[ValidationAlert] = validate_invoice_row(res.row)

                if uploaded_att is not None:
                    try:
                        import cv2  # type: ignore

                        att_path = _tmp_write(uploaded_att)
                        att_bgr = cv2.imread(str(att_path))
                        if att_bgr is None:
                            raise FileNotFoundError("Cannot read attestation image.")
                        paddle = _get_paddle("fr")
                        att_res = paddle.predict(att_bgr)
                        att_items = paddle_predict_to_items(att_res)
                        att_text = "\n".join([(it.text or "").strip() for it in att_items if (it.text or "").strip()])
                        att_fields = extract_attestation_vigilance_fields(att_text)
                        alerts += validate_invoice_vs_attestation(res.row, att_fields)
                        row.update(att_fields)
                    except Exception as e:
                        st.warning(f"Attestation: impossible de traiter ({e}).")

                row["alerts_count"] = str(len(alerts))
                row["alerts_json"] = alerts_to_json(alerts)
                row["alerts_codes"] = ",".join([a.code for a in alerts])

                st.markdown("#### Vérification SIRET (INSEE)")
                supplier_siret = _digits(str(row.get("supplier_siret", "")))
                if supplier_siret:
                    insee = lookup_sirene(supplier_siret)
                    if insee.ok:
                        st.success(f"SIRET trouvé: {supplier_siret}")
                        with st.expander("Détails INSEE (résumé)", expanded=False):
                            st.json(insee.summary)
                    else:
                        if insee.http_status == 404:
                            st.error(
                                f"ALERTE: aucune entreprise trouvée pour ce SIRET (INSEE 404): {supplier_siret}"
                            )
                        elif insee.http_status in (401, 403):
                            st.warning("Vérification INSEE impossible (401/403) — clé API manquante/invalide.")
                        elif insee.http_status:
                            st.warning(f"Vérification INSEE en erreur HTTP {insee.http_status}.")
                        else:
                            st.warning("Vérification INSEE impossible (erreur/identifiant invalide).")
                else:
                    st.info("Pas de SIRET fournisseur détecté par l'OCR.")

                st.markdown("#### Alertes")
                if alerts:
                    worst = "error" if any(a.level == "error" for a in alerts) else "warning"
                    if worst == "error":
                        st.error(f"{len(alerts)} alerte(s) détectée(s).")
                    else:
                        st.warning(f"{len(alerts)} alerte(s) détectée(s).")
                    st.dataframe(_alerts_to_rows(alerts), use_container_width=True)
                else:
                    st.success("Aucune alerte détectée.")

                st.markdown("#### JSON complet")
                st.json(row)

                # Save annotated image to outputs/ and show it
                try:
                    import cv2  # type: ignore

                    out_dir = _project_root() / "outputs"
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_img = out_dir / "annotated_streamlit.jpg"
                    cv2.imwrite(str(out_img), res.annotated_bgr)
                    st.markdown("#### Image annotée")
                    st.image(str(out_img), use_container_width=True)
                    st.download_button(
                        "Télécharger l’image annotée",
                        data=out_img.read_bytes(),
                        file_name=out_img.name,
                        mime="image/jpeg",
                    )
                except Exception as e:
                    st.info(f"Impossible d’écrire l’image annotée: {e}")

                st.download_button(
                    "Télécharger le JSON",
                    data=json.dumps(row, ensure_ascii=False, indent=2).encode("utf-8"),
                    file_name="invoice_row.json",
                    mime="application/json",
                )
            except Exception as e:
                st.error(str(e))


with tab_sirene:
    st.markdown("### Recherche SIREN / SIRET (INSEE)")
    ident = st.text_input("SIREN (9) ou SIRET (14)", value="309634954")
    search = st.button("Rechercher", type="primary")

    if search:
        res = lookup_sirene(ident)
        if not res.ok:
            st.error(f"Erreur INSEE: {res.error} (HTTP={res.http_status})")
            if res.url:
                st.code(res.url)
        else:
            st.success("Trouvé")
            st.json(res.summary)

