from fastapi import APIRouter, Depends
from app.api.v1.auth.dependencies import verify_api_key
from app.api.v1.events.queries import EventQueries

analytics_router = APIRouter()

@analytics_router.get("/flow/{session_id}", tags=["Analytics"])
async def get_event_flow(session_id: str, app: dict = Depends(verify_api_key)):
    """
    Retrieves the ordered event sequence for a session.
    """
    return await EventQueries.get_event_flow(session_id)

@analytics_router.get("/latest/{session_id}", tags=["Analytics"])
async def get_latest_event(session_id: str, app: dict = Depends(verify_api_key)):
    """
    Retrieves the most recent event in a session.
    """
    return await EventQueries.get_latest_event(session_id)

@analytics_router.get("/counts/{session_id}", tags=["Analytics"])
async def get_event_counts(session_id: str, app: dict = Depends(verify_api_key)):
    """
    Retrieves the count of different event types in a session.
    """
    return await EventQueries.get_event_counts(session_id)
