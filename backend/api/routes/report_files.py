import uuid
from datetime import timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.api.rabbitmq import publish_job
from backend.api.config.settings import get_settings
from backend.api.db.session import get_session
from backend.api.db.models.report import Report
from backend.api.db.models.report_file import (
    ReportFile,
    FileType,
    FileCategory,
    FileStatus,
)
from backend.api.minio_client import get_minio_client

router = APIRouter(prefix="/reports/{report_id}/files", tags=["report_files"])
settings = get_settings()


@router.post("/upload")
async def create_presigned_upload_url(
    report_id: int,
    file_type: FileType,
    category: FileCategory,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")

    result = await session.execute(
        select(ReportFile).where(
            ReportFile.report_id == report_id,
            ReportFile.category == category,
        )
    )
    existing_file = result.scalar_one_or_none()
    minio = get_minio_client()

    if existing_file:
        status = getattr(existing_file.status, "value", str(existing_file.status))
        if status == FileStatus.error.value:
            try:
                upload_url = minio.presigned_put_object(
                    bucket_name=existing_file.s3_bucket or settings.minio_bucket,
                    object_name=existing_file.s3_key,
                    expires=timedelta(hours=1),
                )
            except Exception as e:
                raise HTTPException(500, f"Error generating presigned URL: {e}")
            return {
                "file_id": existing_file.id,
                "upload_url": upload_url,
                "s3_key": existing_file.s3_key,
                "s3_bucket": existing_file.s3_bucket,
                "file_type": existing_file.type,
                "category": existing_file.category,
                "status": existing_file.status,
                "message": "Reused existing errored file for retry.",
            }

        if status in (FileStatus.pending.value, FileStatus.processing.value):
            raise HTTPException(409, f"File already in progress ({status}).")
        if status == FileStatus.done.value:
            raise HTTPException(400, "File already completed successfully.")

    s3_key = f"{file_type.lower()}_{uuid.uuid4()}.{file_type}"
    file_record = ReportFile(
        report_id=report_id,
        type=file_type,
        category=category,
        s3_key=s3_key,
        s3_bucket=settings.minio_bucket,
        status=FileStatus.pending,
    )
    session.add(file_record)
    try:
        await session.commit()
        await session.refresh(file_record)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(400, f"Integrity error: {e.orig}")

    try:
        upload_url = minio.presigned_put_object(
            bucket_name=settings.minio_bucket,
            object_name=s3_key,
            expires=timedelta(hours=1),
        )
    except Exception as e:
        raise HTTPException(500, f"Error generating presigned URL: {e}")

    return {
        "file_id": file_record.id,
        "upload_url": upload_url,
        "s3_key": s3_key,
        "s3_bucket": settings.minio_bucket,
        "file_type": file_type,
        "category": category,
        "status": file_record.status,
        "message": "Created new file record.",
    }


@router.get("")
async def list_report_files(
    report_id: int, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(ReportFile).where(ReportFile.report_id == report_id)
    )
    return result.scalars().all()


@router.get("/{file_id}")
async def get_download_url(
    report_id: int,
    file_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ReportFile).where(
            ReportFile.id == file_id, ReportFile.report_id == report_id
        )
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")

    minio = get_minio_client()
    try:
        download_url = minio.presigned_get_object(
            bucket_name=file.s3_bucket or settings.minio_bucket,
            object_name=file.s3_key,
            expires=timedelta(hours=1),
            response_headers={
                "response-content-type": (
                    "text/plain" if file.type == FileType.txt else "application/pdf"
                )
            },
        )
    except Exception as e:
        raise HTTPException(500, f"Error generating download URL: {e}")

    return {"download_url": download_url}


class FileStatusUpdate(BaseModel):
    status: FileStatus
    error_message: str | None = None


@router.patch("/{file_id}/status")
async def update_file_status(
    report_id: int,
    file_id: int,
    payload: FileStatusUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ReportFile).where(
            ReportFile.id == file_id,
            ReportFile.report_id == report_id,
        )
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(404, "File not found")

    file.status = payload.status
    file.error = payload.error_message
    await session.commit()
    await session.refresh(file)

    if file.status == FileStatus.done:
        payload_data = {
            "report_id": file.report_id,
            "file_id": file.id,
            "file_type": file.type,
        }
        if file.category == FileCategory.source:
            background_tasks.add_task(publish_job, payload_data, "extractor")
        elif file.category == FileCategory.extract:
            background_tasks.add_task(publish_job, payload_data, "renderer")

    return {"id": file.id, "status": file.status, "error": file.error}
