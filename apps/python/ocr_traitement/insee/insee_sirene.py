from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


DEFAULT_SIRENE_BASE_URL = "https://api.insee.fr/api-sirene/3.11"


def _digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")


def _http_get_json(url: str, api_key: str) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-INSEE-Api-Key-Integration": api_key,
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        return {"_http_status": int(getattr(e, "code", 0) or 0), "_error": body, "_url": url}


def _extract_unite_legale_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    ul = payload.get("uniteLegale") or payload
    periods = ul.get("periodesUniteLegale") or []
    last = periods[-1] if isinstance(periods, list) and periods else {}

    denom = last.get("denominationUniteLegale") or last.get("nomUniteLegale") or ""
    denom_usuelle = (
        last.get("denominationUsuelle1UniteLegale")
        or last.get("denominationUsuelle2UniteLegale")
        or last.get("denominationUsuelle3UniteLegale")
        or ""
    )

    return {
        "siren": ul.get("siren"),
        "denomination": denom,
        "denomination_usuelle": denom_usuelle,
        "date_creation": ul.get("dateCreationUniteLegale"),
        "etat_administratif": last.get("etatAdministratifUniteLegale"),
        "activite_principale": last.get("activitePrincipaleUniteLegale") or ul.get("activitePrincipaleUniteLegale"),
        "categorie_juridique": last.get("categorieJuridiqueUniteLegale"),
        "nic_siege": last.get("nicSiegeUniteLegale"),
        "statut_diffusion": ul.get("statutDiffusionUniteLegale"),
        "date_dernier_traitement": ul.get("dateDernierTraitementUniteLegale"),
    }


def _extract_etablissement_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    etab = payload.get("etablissement") or payload
    periodes = etab.get("periodesEtablissement") or []
    last = periodes[-1] if isinstance(periodes, list) and periodes else {}

    addr = etab.get("adresseEtablissement") or {}
    libelle_voie = " ".join(
        [
            str(addr.get("numeroVoieEtablissement") or "").strip(),
            str(addr.get("typeVoieEtablissement") or "").strip(),
            str(addr.get("libelleVoieEtablissement") or "").strip(),
        ]
    ).strip()

    return {
        "siret": etab.get("siret"),
        "siren": etab.get("siren"),
        "etat_administratif_etab": last.get("etatAdministratifEtablissement"),
        "date_creation_etab": etab.get("dateCreationEtablissement"),
        "activite_principale_etab": last.get("activitePrincipaleEtablissement"),
        "enseigne": last.get("enseigne1Etablissement")
        or last.get("enseigne2Etablissement")
        or last.get("enseigne3Etablissement"),
        "adresse": libelle_voie,
        "code_postal": addr.get("codePostalEtablissement"),
        "commune": addr.get("libelleCommuneEtablissement"),
    }


@dataclass(frozen=True)
class InseeLookupResult:
    ok: bool
    kind: str  # 'siren'|'siret'
    summary: Dict[str, Any]
    error: Optional[str] = None
    url: Optional[str] = None
    http_status: Optional[int] = None


def lookup_sirene(identifier: str, *, api_key: Optional[str] = None, base_url: Optional[str] = None) -> InseeLookupResult:
    """
    Lookup INSEE SIRENE for SIREN (9 digits) or SIRET (14 digits).

    Credentials:
    - api_key: if not provided, read INSEE_API_KEY_INTEGRATION (or INSEE_API_KEY)
    Base URL:
    - base_url: if not provided, read INSEE_SIRENE_BASE_URL else DEFAULT_SIRENE_BASE_URL
    """

    api_key = (api_key or os.environ.get("INSEE_API_KEY_INTEGRATION") or os.environ.get("INSEE_API_KEY") or "").strip()
    if not api_key:
        return InseeLookupResult(ok=False, kind="unknown", summary={}, error="Missing INSEE_API_KEY_INTEGRATION")

    base_url = (base_url or os.environ.get("INSEE_SIRENE_BASE_URL") or DEFAULT_SIRENE_BASE_URL).strip().rstrip("/")
    d = _digits(identifier)

    if len(d) == 9:
        url = f"{base_url}/siren/{d}"
        payload = _http_get_json(url, api_key)
        if payload.get("_http_status"):
            return InseeLookupResult(
                ok=False,
                kind="siren",
                summary={},
                error=str(payload.get("_error") or ""),
                url=str(payload.get("_url") or url),
                http_status=int(payload.get("_http_status") or 0),
            )
        return InseeLookupResult(ok=True, kind="siren", summary=_extract_unite_legale_summary(payload))

    if len(d) == 14:
        url = f"{base_url}/siret/{d}"
        payload = _http_get_json(url, api_key)
        if payload.get("_http_status"):
            return InseeLookupResult(
                ok=False,
                kind="siret",
                summary={},
                error=str(payload.get("_error") or ""),
                url=str(payload.get("_url") or url),
                http_status=int(payload.get("_http_status") or 0),
            )
        etab_sum = _extract_etablissement_summary(payload)

        # Best-effort unit legal lookup
        ul_sum: Dict[str, Any] = {}
        try:
            siren = str(etab_sum.get("siren") or "")
            if siren and len(_digits(siren)) == 9:
                url_ul = f"{base_url}/siren/{_digits(siren)}"
                ul_payload = _http_get_json(url_ul, api_key)
                if not ul_payload.get("_http_status"):
                    ul_sum = _extract_unite_legale_summary(ul_payload)
        except Exception:
            ul_sum = {}

        merged = {**etab_sum, **{f"ul_{k}": v for k, v in ul_sum.items()}}
        return InseeLookupResult(ok=True, kind="siret", summary=merged)

    return InseeLookupResult(
        ok=False,
        kind="unknown",
        summary={},
        error=f"Identifier must be SIREN(9) or SIRET(14), got {len(d)} digits",
    )

