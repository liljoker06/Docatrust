import json
from datetime import datetime

import requests

from tasks.config.settings import PYTHON_API_URL, CLEAN_BUCKET, DAG_ID
from tasks.utils.db import update_document_status, insert_pipeline_log
from tasks.utils.minio_client import upload_json


def task_ocr(**context):
    """
    Envoie le fichier à la FastAPI Python pour OCR + extraction de champs,
    puis stocke le résultat brut dans la zone clean de MinIO.
    """
    ti                = context["ti"]
    tmp_file_path     = ti.xcom_pull(task_ids="ingest", key="tmp_file_path")
    document_id       = ti.xcom_pull(task_ids="ingest", key="document_id")
    original_filename = ti.xcom_pull(task_ids="ingest", key="original_filename")
    run_id            = context["dag_run"].run_id
    start_time        = datetime.utcnow()

    with open(tmp_file_path, "rb") as file_handle:
        response = requests.post(
            f"{PYTHON_API_URL}/ocr/process",
            files={"file": (original_filename, file_handle)},
            timeout=180,
        )
        response.raise_for_status()

    ocr_data  = response.json().get("data", {})
    clean_key = f"processed/{document_id}/ocr_result.json"

    upload_json(CLEAN_BUCKET, clean_key, json.dumps(ocr_data, ensure_ascii=False))

    update_document_status(document_id, "CLEAN")
    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    insert_pipeline_log(document_id, "RAW", "CLEAN", "SUCCESS", DAG_ID, run_id, duration_ms=duration_ms)

    ti.xcom_push(key="ocr_data",    value=ocr_data)
    ti.xcom_push(key="document_id", value=document_id)
    ti.xcom_push(key="clean_key",   value=clean_key)
