from minio import Minio
from backend.api.config.settings import get_settings
import mimetypes

from backend.api.db.models.report_file import FileType


def get_minio_client() -> Minio:
    settings = get_settings()
    return Minio(
        endpoint=settings.minio_endpoint.replace("http://", "").replace("https://", ""),
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def get_content_type_for_filetype(file_type: FileType) -> str:
    mapping = {
        "pdf": "application/pdf",
        "json": "application/json",
        "txt": "text/plain; charset=utf-8",
    }
    return mapping.get(
        file_type,
        mimetypes.guess_type(f"file.{file_type}")[0] or "application/octet-stream",
    )
