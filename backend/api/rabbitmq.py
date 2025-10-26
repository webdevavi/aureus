import json
import aio_pika
from backend.api.config.settings import get_settings


async def publish_job(payload: dict, queue_name: str):
    settings = get_settings()
    print(settings.rabbitmq_url)
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            settings.rabbitmq_exchange, aio_pika.ExchangeType.DIRECT, durable=True
        )
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=queue_name)

        message = aio_pika.Message(json.dumps(payload).encode())
        await exchange.publish(message, routing_key=queue_name)
        print(f"Queued {queue_name} job for report {payload.get('report_id')}")
