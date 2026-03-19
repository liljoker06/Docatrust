import psycopg2
from tasks.config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def update_document_status(document_id: str, new_status: str) -> None:
    """Met à jour le statut d'un document dans documents_raw."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE documents_raw SET status = %s, updated_at = NOW() WHERE id = %s",
                (new_status, document_id),
            )
        connection.commit()
    finally:
        connection.close()


def insert_pipeline_log(
    document_id: str,
    from_status: str | None,
    to_status: str | None,
    status: str,
    dag_id: str,
    run_id: str,
    error_message: str | None = None,
    duration_ms: int | None = None,
) -> None:
    """Insère un log dans pipeline_logs."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pipeline_logs
                    (id, document_id, from_status, to_status, status,
                     airflow_dag_id, airflow_run_id, error_message, duration_ms, created_at)
                VALUES
                    (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (document_id, from_status, to_status, status, dag_id, run_id, error_message, duration_ms),
            )
        connection.commit()
    finally:
        connection.close()
