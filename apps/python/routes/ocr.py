from fastapi import APIRouter, File, UploadFile

from controllers.ocr import process_invoice, sirene_lookup

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/process")
async def process_invoice_endpoint(file: UploadFile = File(...)):
    return await process_invoice(file)


@router.get("/sirene/{identifier}")
def sirene_lookup_endpoint(identifier: str):
    return sirene_lookup(identifier)
