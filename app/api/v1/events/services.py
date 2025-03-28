import json
import aio_pika
from app.core.config import settings
from app.api.v1.events.models import EventModel
from fastapi.encoders import jsonable_encoder

class EventQueue:
    @staticmethod
    async def push_event(event: EventModel):
        """
        Push event into RabbitMQ queue for async processing.
        """
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("event_queue", durable=True)

            event_data = json.dumps(jsonable_encoder(event.model_dump()))
            await channel.default_exchange.publish(
                aio_pika.Message(body=event_data.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue.name,
            )
        
        return {"message": "Event queued successfully", "event_id": event.event_id}
