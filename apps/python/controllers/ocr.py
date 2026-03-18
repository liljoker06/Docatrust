from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ocr_traitement.insee.insee_sirene import lookup_sirene
from ocr_traitement.pipeline import process_invoice_image


async def process_invoice(file: UploadFile) -> dict:
    suffix = Path(file.filename or "file").suffix or ".jpg"
    content = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(content)
        tmp_path = Path(f.name)

    try:
        result = process_invoice_image(tmp_path, enrich_insee=True)
        return {"status": "ok", "data": dict(result.row)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


def sirene_lookup(identifier: str) -> dict:
    result = lookup_sirene(identifier)
    if not result.ok:
        raise HTTPException(status_code=404, detail=result.error)
    return {"status": "ok", "data": result.summary}
