import asyncio
import multiprocessing as mp
import shutil
import os
import json
from pathlib import Path
from typing import Optional

from backend.api.db.models.report_file import FileType
from backend.workers.extractor.utils.process_pdf import process_pdf
from backend.workers.extractor.utils.report_formatter import generate_report
from backend.workers.extractor.config.settings import get_settings
from backend.workers.extractor.utils.api import (
    fetch_presigned_download,
    download_file,
    create_presigned_upload,
    get_report_details,
    upload_json,
    update_file_status,
    FileCategory,
    FileStatus,
)
from backend.workers.extractor.utils.openai_vision import extract_charts_batch
from backend.workers.extractor.utils.render_page import preprocess_for_vision
from backend.workers.extractor.utils.text_extractor import extract_text_from_txt


mp.set_start_method("spawn", force=True)

MAX_IMAGES_PER_BATCH = 5


async def extract_job(report_id: int, source_file_id: int, source_file_type: FileType):
    print(f"Starting extractor for report {report_id}, source file {source_file_id}")

    settings = get_settings()
    tmp_root = Path("tmp")
    downloads_dir = tmp_root / "downloads"
    output_dir = tmp_root / "output"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"report_{report_id}_extract.json"

    extract_file_id: Optional[int] = None

    try:
        upload_info = await create_presigned_upload(
            settings.api_base_url,
            report_id,
            FileType.json,
            FileCategory.extract,
        )
        extract_file_id = upload_info["file_id"]

        assert (
            extract_file_id is not None
        ), "extract_file_id missing before status update"
        await update_file_status(
            settings.api_base_url, report_id, extract_file_id, FileStatus.processing
        )

        report = await get_report_details(settings.api_base_url, report_id)
        print(f"Processing report for {report['company_name']}")

        presigned_url = await fetch_presigned_download(
            settings.api_base_url, report_id, source_file_id
        )
        file_path = (
            downloads_dir
            / f"report_{report_id}_file_{source_file_id}.{source_file_type}"
        )
        await download_file(presigned_url, str(file_path))

        print(f"Starting extraction for: {file_path} ({source_file_type})")

        if source_file_type == FileType.txt:
            data = extract_text_from_txt(str(file_path))
        elif source_file_type == FileType.pdf:
            data = process_pdf(str(file_path), max_workers=settings.max_workers)
        else:
            raise ValueError(f"Unsupported file type: {source_file_type}")

        if not data:
            raise ValueError(
                f"No extractable content found in {source_file_type.upper()} file"
            )

        compressed_pages = []
        for page in [p for p in data if p.get("needs_vision")]:
            compressed_path = preprocess_for_vision(page["img_path"])
            page["compressed_path"] = compressed_path
            sz = os.path.getsize(compressed_path)
            compressed_pages.append((page, sz))

        batches, batch, current_bytes = [], [], 0
        for page, sz in compressed_pages:
            if len(batch) >= MAX_IMAGES_PER_BATCH or current_bytes + sz > 900_000:
                batches.append(batch)
                batch, current_bytes = [], 0
            batch.append(page)
            current_bytes += sz
        if batch:
            batches.append(batch)

        print(f"Vision batches prepared: {len(batches)}")
        for idx, batch in enumerate(batches, 1):
            paths = [p["compressed_path"] for p in batch]
            print(f"Analyzing batch {idx}/{len(batches)} ({len(paths)} pages)...")
            try:
                res = extract_charts_batch(paths)
                for p, r in zip(batch, res):
                    p["chart_json"] = r
            except Exception as e:
                print(f"Vision batch {idx} failed: {e}")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved extracted data to {json_path}")

        print("Generating report artifact...")
        report_path = await asyncio.to_thread(
            generate_report, str(json_path), company_name=report["company_name"]
        )
        print(f"Report artifact at {report_path}")

        await upload_json(upload_info["upload_url"], report_path)

        assert (
            extract_file_id is not None
        ), "extract_file_id missing before status update"
        await update_file_status(
            settings.api_base_url, report_id, extract_file_id, FileStatus.done
        )

        print(f"Report {report_id} processed successfully")

    except Exception as e:
        err_msg = str(e)
        print(f"Extractor failed for report {report_id}: {err_msg}")

        if extract_file_id is not None:
            try:
                await update_file_status(
                    settings.api_base_url,
                    report_id,
                    extract_file_id,
                    FileStatus.error,
                    error_message=err_msg[:5000],
                )
            except Exception as e2:
                print(f"Failed to mark extract file as error: {e2}")
        else:
            print(
                "Extractor failed before extract file creation; skipping status update."
            )

    finally:
        try:
            shutil.rmtree(tmp_root, ignore_errors=True)
            print("Cleanup complete.")
        except Exception as e:
            print(f"Cleanup failed: {e}")
