from fastapi import APIRouter, Depends, Request
from app.api.v1.sdk.auth import verify_sdk_key
from app.api.v1.events.models import EventModel
from app.api.v1.events.services import EventQueue

event_router = APIRouter()

@event_router.post("/ingest", tags=["Events"])
async def ingest_event(event: EventModel, app_id: str = Depends(verify_sdk_key)):
    """
    Receives an event from the SDK and pushes it to RabbitMQ.
    """
    event.app_id = app_id  # Associate event with the authenticated app
    return await EventQueue.push_event(event)