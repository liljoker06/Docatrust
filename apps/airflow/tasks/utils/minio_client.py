import io

from minio import Minio
from tasks.config.settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY


def get_client() -> Minio:
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


def download_file(bucket: str, object_key: str, destination_path: str) -> None:
    """Télécharge un objet MinIO vers un fichier local."""
    get_client().fget_object(bucket, object_key, destination_path)


def upload_json(bucket: str, object_key: str, payload: str) -> None:
    """Envoie une chaîne JSON dans un bucket MinIO."""
    encoded = payload.encode("utf-8")
    get_client().put_object(
        bucket,
        object_key,
        io.BytesIO(encoded),
        len(encoded),
        content_type="application/json",
    )
