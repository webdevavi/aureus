from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.api.db.session import get_session
from backend.api.db.models.report import Report
from backend.api.db.models.report_file import FileCategory, FileStatus
from backend.api.rabbitmq import publish_job


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(
    company_name: str, session: AsyncSession = Depends(get_session)
):
    report = Report(company_name=company_name)
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return {
        "id": report.id,
        "company_name": report.company_name,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


@router.get("", status_code=status.HTTP_200_OK)
async def list_reports(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Report))
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "company_name": r.company_name,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in reports
    ]


@router.get("/{report_id}", status_code=status.HTTP_200_OK)
async def get_report(report_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    return {
        "id": report.id,
        "company_name": report.company_name,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    await session.delete(report)
    await session.commit()
    return {"detail": "Report deleted successfully"}


@router.post("/{report_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_report_processing(
    report_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Report).options(selectinload(Report.files)).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")

    files = {f.category.value: f for f in report.files}

    source_file = files.get(FileCategory.source.value)
    extract_file = files.get(FileCategory.extract.value)
    output_file = files.get(FileCategory.output.value)

    if not source_file:
        raise HTTPException(400, "Cannot retry: no source file uploaded yet.")

    def status_val(file):
        return getattr(file.status, "value", str(file.status)) if file else None

    ext_status = status_val(extract_file)
    out_status = status_val(output_file)

    if extract_file is None or ext_status == FileStatus.error.value:
        payload = {"report_id": report.id, "file_id": source_file.id}
        background_tasks.add_task(publish_job, payload, "extractor")
        return {
            "report_id": report.id,
            "retry_stage": "extractor",
            "queued": True,
            "message": "Report re-queued for extractor processing.",
        }

    if ext_status == FileStatus.done.value:
        if output_file is None or out_status == FileStatus.error.value:
            payload = {"report_id": report.id, "file_id": extract_file.id}
            background_tasks.add_task(publish_job, payload, "renderer")
            return {
                "report_id": report.id,
                "retry_stage": "renderer",
                "queued": True,
                "message": "Report re-queued for renderer processing.",
            }

    if ext_status in (FileStatus.pending.value, FileStatus.processing.value):
        raise HTTPException(409, "Extraction already in progress.")
    if out_status in (FileStatus.pending.value, FileStatus.processing.value):
        raise HTTPException(409, "Rendering already in progress.")

    raise HTTPException(
        400,
        "Nothing to retry: all stages completed successfully.",
    )
