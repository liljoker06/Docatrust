from fastapi import FastAPI, HTTPException
import subprocess
import sys
import os

app = FastAPI()

SCRIPTS_DIR = "/app/data/scripts"

@app.get("/health")
def health():
    return {"status": "ok", "service": "python"}

def _run_script(script_name: str):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
    return {"status": "ok", "output": result.stdout}

@app.post("/generate/devis")
def generate_devis():
    return _run_script("generate_devis.py")

@app.post("/generate/factures")
def generate_factures():
    return _run_script("generate_factures.py")

@app.post("/generate/factures-erronees")
def generate_factures_erronees():
    return _run_script("generate_factures_erronees.py")

@app.post("/generate/scans")
def generate_scans():
    return _run_script("generate_scans.py")
