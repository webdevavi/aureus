import os
import aiohttp
from typing import Any
from backend.api.db.models.report_file import FileCategory, FileStatus, FileType
from backend.workers.extractor.config.settings import get_settings

settings = get_settings()


async def get_report_details(api_base_url: str, report_id: int) -> dict[str, Any]:
    url = f"{api_base_url}/reports/{report_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"Failed to fetch report details: {resp.status} - {text}"
                )

            data = await resp.json()
            if not isinstance(data, dict) or "id" not in data:
                raise RuntimeError("Malformed report details response")

            print(f"Retrieved report {data['id']} ({data.get('company_name', '-')})")
            return data


async def fetch_presigned_download(
    api_base_url: str, report_id: int, file_id: int
) -> str:
    url = f"{api_base_url}/reports/{report_id}/files/{file_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"Failed to get download URL: {resp.status} - {text}"
                )
            data = await resp.json()
            return data.get("download_url")


async def download_file(download_url: str, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"Download failed: {resp.status} - {text}")
            with open(dest_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)
    print(f"Downloaded → {dest_path}")


async def create_presigned_upload(
    api_base_url: str,
    report_id: int,
    file_type: FileType,
    category: FileCategory,
) -> dict[str, Any]:
    url = f"{api_base_url}/reports/{report_id}/files/upload"
    params = {
        "file_type": file_type.value,
        "category": category.value,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"Failed to create presigned upload URL: {resp.status} - {text}"
                )
            data = await resp.json()
            print(f"Created pending file (id={data['file_id']}) for {category.value}")
            return data


async def upload_json(upload_url: str, json_path: str):
    async with aiohttp.ClientSession() as session:
        with open(json_path, "rb") as f:
            resp = await session.put(
                upload_url,
                data=f,
                headers={"Content-Type": "application/json"},
            )
            if resp.status not in (200, 201):
                text = await resp.text()
                raise RuntimeError(f"Upload failed: {resp.status} - {text}")
    print("Uploaded JSON to MinIO successfully.")


async def update_file_status(
    api_base_url: str,
    report_id: int,
    file_id: int,
    status: FileStatus,
    error_message: str | None = None,
):
    url = f"{api_base_url}/reports/{report_id}/files/{file_id}/status"
    payload = {"status": status.value}
    if error_message:
        payload["error_message"] = error_message

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=payload) as resp:
            if resp.status not in (200, 204):
                text = await resp.text()
                raise RuntimeError(
                    f"Failed to update file status: {resp.status} - {text}"
                )
            print(f"File {file_id} → {status.value}")
