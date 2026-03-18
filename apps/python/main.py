from fastapi import FastAPI

from routes.generation import router as generation_router
from routes.ocr import router as ocr_router

app = FastAPI(title="Pyra Python API", version="1.0.0")

app.include_router(generation_router)
app.include_router(ocr_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "python"}
