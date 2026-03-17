from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import streamlit as st


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _ensure_imports():
    # Run without installing the package: add src/ to path
    import sys

    sys.path.insert(0, str(_project_root() / "src"))

    from ocr_traitement.insee_sirene import lookup_sirene  # noqa: F401
    from ocr_traitement.pipeline import process_invoice_image  # noqa: F401


_ensure_imports()

from ocr_traitement.insee_sirene import lookup_sirene
from ocr_traitement.pipeline import process_invoice_image


st.set_page_config(page_title="Docatrust OCR", page_icon="🧾", layout="wide")

st.markdown("## Docatrust — OCR + Vérifications (INSEE)")

with st.sidebar:
    st.markdown("### Configuration")
    st.code(f"INSEE_API_KEY_INTEGRATION={'SET' if os.environ.get('INSEE_API_KEY_INTEGRATION') else 'NOT SET'}")
    base = os.environ.get("INSEE_SIRENE_BASE_URL", "https://api.insee.fr/api-sirene/3.11")
    st.text_input("INSEE_SIRENE_BASE_URL (env)", value=base, disabled=True)
    st.caption("Charge ton `.env` avant de lancer Streamlit (ou exporte les variables).")


tab_upload, tab_sirene = st.tabs(["Upload facture (OCR)", "Recherche Sirene (INSEE)"])

with tab_upload:
    st.markdown("### Upload d’une facture (image)")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        uploaded = st.file_uploader("Image facture (jpg/png/webp)", type=["jpg", "jpeg", "png", "webp"])
        run = st.button("Lancer le traitement", type="primary", disabled=(uploaded is None))

        if uploaded is not None:
            st.image(uploaded, caption="Facture uploadée", use_container_width=True)

    with col2:
        if run and uploaded is not None:
            try:
                suffix = Path(uploaded.name).suffix or ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                    f.write(uploaded.getvalue())
                    tmp_path = Path(f.name)

                res = process_invoice_image(tmp_path, enrich_insee=True)

                st.markdown("### Résultat")
                st.markdown("#### Champs (CSV row)")
                st.json(res.row)

                # Show fraud alert if any
                fraud = res.row.get("fraud_alert")
                if fraud in ("true", "unknown"):
                    st.warning(f"Fraud alert: {fraud} — {res.row.get('fraud_reason','')}")

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
                    data=json.dumps(res.row, ensure_ascii=False, indent=2).encode("utf-8"),
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

