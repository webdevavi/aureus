import os
import aiohttp
from backend.api.db.models.report_file import FileCategory, FileStatus, FileType
from backend.workers.renderer.config.settings import get_settings

settings = get_settings()


async def fetch_presigned_download(
    api_base_url: str, report_id: int, file_id: int
) -> str:
    url = f"{api_base_url}/reports/{report_id}/files/{file_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(
                    f"Failed to get presigned download URL: {resp.status}"
                )
            data = await resp.json()
            download_url = data.get("download_url")
            if not download_url:
                raise RuntimeError("Response missing download_url field")
            return download_url


async def download_file(download_url: str, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Download failed: {resp.status}")
            with open(dest_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)
    print(f"Downloaded → {dest_path}")


async def create_presigned_upload(
    api_base_url: str,
    report_id: int,
    file_type: FileType,
    category: FileCategory,
) -> dict:
    url = f"{api_base_url}/reports/{report_id}/files/upload"
    params = {"file_type": file_type.value, "category": category.value}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(
                    f"Failed to create presigned upload URL: {resp.status} - {text}"
                )
            data = await resp.json()
            if "upload_url" not in data or "file_id" not in data:
                raise RuntimeError("Invalid response: missing upload_url or file_id")
            print(f"Created file record id={data['file_id']} ({category.value})")
            return data


async def upload_file(upload_url: str, file_path: str, content_type: str):
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            resp = await session.put(
                upload_url, data=f, headers={"Content-Type": content_type}
            )
            if resp.status not in (200, 201):
                text = await resp.text()
                raise RuntimeError(f"Upload failed: {resp.status} - {text}")
    print(f"Uploaded {os.path.basename(file_path)} successfully.")


async def upload_pdf(upload_url: str, pdf_path: str):
    await upload_file(upload_url, pdf_path, "application/pdf")


async def upload_json(upload_url: str, json_path: str):
    await upload_file(upload_url, json_path, "application/json")


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
