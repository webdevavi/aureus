from aio_pika.abc import AbstractIncomingMessage
import asyncio
import json
from backend.api.db.models.report_file import FileType
from backend.workers.extractor.extract_job import extract_job


async def process_message(message: AbstractIncomingMessage) -> None:
    try:
        payload = json.loads(message.body)
        print(f"Received message: {payload}")

        await message.ack()

        async def _run():
            try:
                payload = json.loads(message.body)
                report_id = payload["report_id"]
                file_id = payload["file_id"]
                file_type = FileType(payload.get("file_type", "pdf"))
                await extract_job(report_id, file_id, file_type)
                print(f"Successfully processed {payload}")
            except Exception as e:
                print(f"Error in extract_job: {e}")

        asyncio.create_task(_run())

    except Exception as e:
        print(f"Error processing message: {e}")
        try:
            await message.ack()
        except Exception as ack_err:
            print(f"Failed to ack message after error: {ack_err}")
