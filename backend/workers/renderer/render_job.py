import multiprocessing as mp
import shutil
from pathlib import Path
from typing import Optional
from backend.workers.renderer.config.settings import get_settings
from backend.workers.renderer.utils.api import (
    fetch_presigned_download,
    download_file,
    create_presigned_upload,
    upload_pdf,
    update_file_status,
    FileType,
    FileStatus,
    FileCategory,
)
from backend.workers.renderer.utils.report_generator import generate_report

mp.set_start_method("spawn", force=True)


async def render_job(report_id: int, extract_file_id: int):
    print(f"Starting renderer for report {report_id}, extract file {extract_file_id}")

    settings = get_settings()
    tmp_root = Path("tmp")
    downloads_dir = tmp_root / "downloads"
    output_dir = tmp_root / "output"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file_id: Optional[int] = None

    try:
        print("Fetching presigned download URL for extracted JSON...")
        presigned_url = await fetch_presigned_download(
            settings.api_base_url, report_id, extract_file_id
        )

        json_path = downloads_dir / f"report_{report_id}_extract_{extract_file_id}.json"
        print(f"Downloading extracted JSON → {json_path}")
        await download_file(presigned_url, str(json_path))

        print("Creating output file record...")
        upload_info = await create_presigned_upload(
            settings.api_base_url,
            report_id,
            FileType.pdf,
            FileCategory.output,
        )
        output_file_id = upload_info["file_id"]

        assert output_file_id is not None, "output_file_id missing before status update"
        await update_file_status(
            settings.api_base_url, report_id, output_file_id, FileStatus.processing
        )

        print("Generating formatted PDF report...")
        try:
            pdf_path = await generate_report(str(json_path))
            print(f"PDF generated at {pdf_path}")
        except Exception as e:
            raise RuntimeError(f"Report generation failed: {e}")

        print("Uploading PDF to object store...")
        await upload_pdf(upload_info["upload_url"], pdf_path)
        print("Upload complete.")

        assert output_file_id is not None, "output_file_id missing before status update"
        await update_file_status(
            settings.api_base_url, report_id, output_file_id, FileStatus.done
        )

        print(f"Report {report_id} rendered successfully")

    except Exception as e:
        err_msg = str(e)
        print(f"Renderer failed for report {report_id}: {err_msg}")
        if output_file_id:
            try:
                await update_file_status(
                    settings.api_base_url,
                    report_id,
                    output_file_id,
                    FileStatus.error,
                    error_message=err_msg[:5000],
                )
            except Exception as e2:
                print(f"Failed to mark output file as error: {e2}")
        else:
            print(
                "Renderer failed before output file creation; skipping status update."
            )

    finally:
        try:
            shutil.rmtree(tmp_root, ignore_errors=True)
            print("Cleanup complete.")
        except Exception as e:
            print(f"Cleanup failed: {e}")
