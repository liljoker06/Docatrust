import json
from datetime import datetime


def task_validate(**context):
    """
    Vérifie les incohérences dans les données OCR :
    - Alertes remontées par le pipeline Python (TVA, montants, etc.)
    - SIRET introuvable dans INSEE (fraude potentielle)
    - Attestation expirée
    """
    ti          = context["ti"]
    ocr_data    = ti.xcom_pull(task_ids="ocr", key="ocr_data")
    document_id = ti.xcom_pull(task_ids="ocr", key="document_id")

    validation_alerts = []

    # Alertes remontées directement par le pipeline OCR Python
    raw_alerts = ocr_data.get("alerts_json", "[]")
    if isinstance(raw_alerts, str):
        try:
            ocr_alerts = json.loads(raw_alerts)
        except json.JSONDecodeError:
            ocr_alerts = []
    else:
        ocr_alerts = raw_alerts if isinstance(raw_alerts, list) else []
    validation_alerts.extend(ocr_alerts)

    # SIRET non trouvé dans INSEE → fraude potentielle
    if ocr_data.get("fraud_alert") == "true":
        validation_alerts.append({
            "code":    "FRAUD_SIRET_NOT_FOUND",
            "level":   "ERROR",
            "message": "SIRET introuvable dans la base INSEE — document potentiellement frauduleux.",
        })

    # Attestation expirée
    expiration_date_str = ocr_data.get("expiration_date") or ocr_data.get("date_expiration")
    if expiration_date_str:
        try:
            expiration_date = datetime.fromisoformat(str(expiration_date_str))
            if expiration_date < datetime.utcnow():
                validation_alerts.append({
                    "code":    "ATTESTATION_EXPIRED",
                    "level":   "ERROR",
                    "message": f"Attestation expirée depuis le {expiration_date_str}.",
                })
        except ValueError:
            pass

    ti.xcom_push(key="validation_alerts", value=validation_alerts)
    ti.xcom_push(key="document_id",       value=document_id)
