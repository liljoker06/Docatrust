"""
DAG : document_pipeline
Déclenché par l'API Node.js après chaque upload de document.

Flux : ingest → ocr → validate → save_results
"""

import sys
import os

# Rend le dossier tasks/ accessible depuis le DAG (/opt/airflow/tasks)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from tasks.ingest       import task_ingest
from tasks.ocr          import task_ocr
from tasks.validate     import task_validate
from tasks.save_results import task_save_results
from tasks.utils.db     import update_document_status, insert_pipeline_log
from tasks.config.settings import DAG_ID

# ─── Callback d'échec ──────────────────────────────────────────────────────

def on_task_failure(context):
    """Log l'échec en base et passe le document en statut ERROR."""
    document_id = (context["dag_run"].conf or {}).get("document_id")
    if not document_id:
        return
    error_message = str(context.get("exception", "Erreur inconnue"))[:500]
    update_document_status(document_id, "ERROR")
    insert_pipeline_log(
        document_id, None, "ERROR", "FAILURE",
        DAG_ID, context["dag_run"].run_id,
        error_message=error_message,
    )

# ─── Définition du DAG ────────────────────────────────────────────────────

default_args = {
    "owner":                     "pyra",
    "retries":                   3,
    "retry_delay":               timedelta(seconds=60),
    "retry_exponential_backoff": True,
    "on_failure_callback":       on_task_failure,
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Pipeline de traitement de documents : OCR → Validation → Stockage structuré",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["pyra", "ocr", "pipeline"],
) as dag:

    ingest = PythonOperator(
        task_id="ingest",
        python_callable=task_ingest,
    )

    ocr = PythonOperator(
        task_id="ocr",
        python_callable=task_ocr,
    )

    validate = PythonOperator(
        task_id="validate",
        python_callable=task_validate,
    )

    save_results = PythonOperator(
        task_id="save_results",
        python_callable=task_save_results,
    )

    ingest >> ocr >> validate >> save_results
