from fastapi import APIRouter, Depends
from app.api.v1.auth.dependencies import get_current_user
from app.api.v1.apps.models import AppCreateRequest
from app.api.v1.apps.services import AppService

app_router = APIRouter()

@app_router.post("/create", tags=["Apps"])
async def create_app(app_data: AppCreateRequest, user: dict = Depends(get_current_user)):
    """
    Creates a new App and generates a unique API key.
    """
    return await AppService.create_app(user["user_id"], app_data)

@app_router.get("/{app_id}", tags=["Apps"])
async def get_app(app_id: str, user: dict = Depends(get_current_user)):
    """
    Retrieves details of a specific App by App ID.
    """
    return await AppService.get_app(app_id, user["user_id"])

@app_router.get("/", tags=["Apps"])
async def get_user_apps(user: dict = Depends(get_current_user)):
    """
    Retrieves all Apps owned by the authenticated user.
    """
    return await AppService.get_user_apps(user["user_id"])