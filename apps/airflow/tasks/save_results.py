import json
from datetime import datetime

from tasks.config.settings import CURATED_BUCKET, DAG_ID
from tasks.utils.db import update_document_status, insert_pipeline_log
from tasks.utils.minio_client import upload_json


def task_save_results(**context):
    """
    Assemble le JSON final (champs extraits + alertes),
    le stocke dans la zone curated de MinIO,
    et met à jour le statut du document en base.
    """
    ti                = context["ti"]
    ocr_data          = ti.xcom_pull(task_ids="ocr",      key="ocr_data")
    validation_alerts = ti.xcom_pull(task_ids="validate", key="validation_alerts")
    document_id       = ti.xcom_pull(task_ids="validate", key="document_id")
    run_id            = context["dag_run"].run_id
    start_time        = datetime.utcnow()

    curated_payload = {
        "document_id":      document_id,
        "extracted_fields": ocr_data,
        "alerts":           validation_alerts,
        "alerts_count":     len(validation_alerts),
        "processed_at":     datetime.utcnow().isoformat(),
    }

    curated_key = f"processed/{document_id}/curated.json"
    upload_json(CURATED_BUCKET, curated_key, json.dumps(curated_payload, ensure_ascii=False))

    update_document_status(document_id, "CURATED")
    duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    insert_pipeline_log(document_id, "CLEAN", "CURATED", "SUCCESS", DAG_ID, run_id, duration_ms=duration_ms)
