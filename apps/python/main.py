from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.generation import router as generation_router
from routes.ocr import router as ocr_router

app = FastAPI(title="Pyra Python API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation_router)
app.include_router(ocr_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "python"}
