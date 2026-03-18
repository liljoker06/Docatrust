FROM apache/airflow:2.9.3-python3.11

USER airflow

# For SQLAlchemy connection postgresql+psycopg2://...
RUN pip install --no-cache-dir psycopg2-binary

ENV AIRFLOW_HOME=/opt/airflow
WORKDIR /opt/airflow

