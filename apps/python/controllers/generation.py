from __future__ import annotations

import os
import subprocess
import sys

from fastapi import HTTPException

SCRIPTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "generation"))


def run_script(script_name: str) -> dict:
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
    return {"status": "ok", "output": result.stdout}
