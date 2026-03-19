import os

PYTHON_API_URL   = os.environ.get("PYTHON_API_URL",   "http://python:8000")

MINIO_ENDPOINT   = os.environ.get("MINIO_ENDPOINT",   "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")

DB_HOST     = os.environ.get("DB_HOST",     "postgres")
DB_PORT     = int(os.environ.get("DB_PORT", "5432"))
DB_NAME     = os.environ.get("DB_NAME",     "pyra_data")
DB_USER     = os.environ.get("DB_USER",     "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

RAW_BUCKET     = "raw"
CLEAN_BUCKET   = "clean"
CURATED_BUCKET = "curated"

DAG_ID = "document_pipeline"
