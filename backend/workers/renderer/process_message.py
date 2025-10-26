from aio_pika.abc import AbstractIncomingMessage
import json
from backend.workers.renderer.render_job import render_job


async def process_message(message: AbstractIncomingMessage):
    try:
        payload = json.loads(message.body)
        print(f"Received message: {payload}")

        await message.ack()

        await render_job(payload["report_id"], payload["file_id"])
        print(f"Successfully processed {payload}")

    except Exception as e:
        print(f"Error processing message: {e}")
        try:
            await message.ack()
        except Exception as ack_err:
            print(f"Failed to ack message after error: {ack_err}")
