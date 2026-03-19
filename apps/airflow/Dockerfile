FROM apache/airflow:2.9.3-python3.11

USER airflow

RUN pip install --no-cache-dir psycopg2-binary minio requests

ENV AIRFLOW_HOME=/opt/airflow
WORKDIR /opt/airflow

