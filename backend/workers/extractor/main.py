import asyncio
import aio_pika
from backend.workers.extractor.config.settings import get_settings
from backend.workers.extractor.process_message import process_message


async def main():
    print("extractor worker starting...")
    settings = get_settings()

    connection = await aio_pika.connect_robust(
        settings.rabbitmq_url,
        timeout=15,
        client_properties={"connection_name": "extractor_worker"},
        reconnect_interval=5,
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            settings.rabbitmq_exchange, aio_pika.ExchangeType.DIRECT, durable=True
        )

        queue = await channel.declare_queue("extractor", durable=True)
        await queue.bind(exchange, routing_key="extractor")

        await queue.consume(process_message, no_ack=False)
        print("Listening on 'extractor' queue...")

        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            print("Graceful shutdown requested.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped manually")
