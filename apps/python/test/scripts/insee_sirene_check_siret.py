#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict


# Mode "clé d'API d'intégration" (pas OAuth)
# D'après la doc: header `X-INSEE-Api-Key-Integration: ...`
DEFAULT_SIRENE_BASE_URL = "https://api.insee.fr/api-sirene/3.11"


def _only_digits(s: str) -> str:
    import re

    return re.sub(r"\D+", "", s or "")


class InseeSireneClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_SIRENE_BASE_URL,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def _get(self, path: str) -> Dict[str, Any]:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        req = urllib.request.Request(
            url,
            headers={
                "X-INSEE-Api-Key-Integration": self.api_key,
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            # Return structured error for easier debugging in CLI output
            return {
                "_http_status": int(getattr(e, "code", 0) or 0),
                "_error": body,
                "_url": url,
            }

    def verify_siret(self, siret: str) -> Dict[str, Any]:
        """
        Vérifie un SIRET via l'API SIRENE v3.11:
          GET /siret/{siret}

        Retour:
          - ok: bool
          - status: 'found'|'not_found'|'invalid'
          - siret: normalized digits
          - details: payload (etablissement si présent)
        """
        s = _only_digits(siret)
        if len(s) != 14:
            return {"ok": False, "status": "invalid", "siret": s, "details": None}

        payload = self._get(f"siret/{s}")
        if payload.get("_http_status"):
            code = int(payload.get("_http_status") or 0)
            if code == 404:
                err = payload.get("_error") or ""
                if isinstance(err, str) and "url deprecated" in err.lower():
                    return {
                        "ok": False,
                        "status": "deprecated",
                        "siret": s,
                        "details": err,
                        "hint": "L'endpoint semble déprécié. Vérifie l'URL dans le portail INSEE et force INSEE_SIRENE_BASE_URL si besoin.",
                    }
                return {"ok": False, "status": "not_found", "siret": s, "details": payload.get("_error")}
            if code in (401, 403):
                return {"ok": False, "status": "unauthorized", "siret": s, "details": payload.get("_error")}
            return {"ok": False, "status": f"http_{code}", "siret": s, "details": payload.get("_error")}

        etab = payload.get("etablissement")
        return {"ok": True, "status": "found", "siret": s, "details": etab if etab else payload}

    def verify_siren(self, siren: str) -> Dict[str, Any]:
        s = _only_digits(siren)
        if len(s) != 9:
            return {"ok": False, "status": "invalid", "siren": s, "details": None}

        payload = self._get(f"siren/{s}")
        if payload.get("_http_status"):
            code = int(payload.get("_http_status") or 0)
            if code == 404:
                err = payload.get("_error") or ""
                if isinstance(err, str) and "url deprecated" in err.lower():
                    return {
                        "ok": False,
                        "status": "deprecated",
                        "siren": s,
                        "details": err,
                        "hint": "L'endpoint semble déprécié. Vérifie l'URL dans le portail INSEE et force INSEE_SIRENE_BASE_URL si besoin.",
                    }
                return {"ok": False, "status": "not_found", "siren": s, "details": payload.get("_error")}
            if code in (401, 403):
                return {"ok": False, "status": "unauthorized", "siren": s, "details": payload.get("_error")}
            return {"ok": False, "status": f"http_{code}", "siren": s, "details": payload.get("_error")}

        ul = payload.get("uniteLegale")
        return {"ok": True, "status": "found", "siren": s, "details": ul if ul else payload}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage:")
        print("  python3 scripts/insee_sirene_check_siret.py <SIRET>")
        print("  python3 scripts/insee_sirene_check_siret.py --siren <SIREN>")
        return 2

    api_key = os.environ.get("INSEE_API_KEY_INTEGRATION", "").strip() or os.environ.get("INSEE_API_KEY", "").strip()
    if not api_key:
        print("Missing env var: INSEE_API_KEY_INTEGRATION (or INSEE_API_KEY)")
        return 2

    base_url = os.environ.get("INSEE_SIRENE_BASE_URL", DEFAULT_SIRENE_BASE_URL).strip() or DEFAULT_SIRENE_BASE_URL
    cli = InseeSireneClient(api_key=api_key, base_url=base_url)

    if argv[0] == "--siren":
        if len(argv) < 2:
            print("Missing SIREN after --siren")
            return 2
        res = cli.verify_siren(argv[1])
    else:
        res = cli.verify_siret(argv[0])

    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

