import os
import tempfile
from datetime import datetime

from tasks.config.settings import RAW_BUCKET, DAG_ID
from tasks.utils.db import insert_pipeline_log
from tasks.utils.minio_client import download_file


def task_ingest(**context):
    """
    Télécharge le fichier brut depuis MinIO (zone raw)
    et le place dans un fichier temporaire pour les tâches suivantes.
    """
    dag_run_conf      = context["dag_run"].conf or {}
    document_id       = dag_run_conf["document_id"]
    object_key        = dag_run_conf["object_key"]
    run_id            = context["dag_run"].run_id
    start_time        = datetime.utcnow()

    original_filename = object_key.split("/")[-1]
    tmp_file_path     = os.path.join(tempfile.gettempdir(), f"{document_id}_{original_filename}")

    download_file(RAW_BUCKET, object_key, tmp_file_path)

    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    insert_pipeline_log(document_id, None, "RAW", "SUCCESS", DAG_ID, run_id, duration_ms=duration_ms)

    context["ti"].xcom_push(key="tmp_file_path",      value=tmp_file_path)
    context["ti"].xcom_push(key="document_id",        value=document_id)
    context["ti"].xcom_push(key="original_filename",  value=original_filename)
