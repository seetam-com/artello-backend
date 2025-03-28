from fastapi import APIRouter, Depends
from app.api.v1.auth.services import sync_user
from app.api.v1.auth.dependencies import verify_token, require_role, get_current_user, verify_api_key
from app.api.v1.auth.schemas import UserResponse, LoginResponse
from app.api.v1.auth.rbac import UserRole
from app.api.v1.auth.apikeys import APIKeyService

auth_router = APIRouter()

@auth_router.get("/test", tags=["Authentication"])
async def get_current_user(auth_payload: dict = Depends(verify_token)):
    """
    Retrieves the currently authenticated user.
    """
    return auth_payload

@auth_router.get("/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user(auth_payload: dict = Depends(verify_token)):
    """
    Retrieves the currently authenticated user.
    """
    user = await sync_user(auth_payload)
    return user

@auth_router.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login(auth_payload: dict = Depends(verify_token)):
    """
    Handles user login by validating Clerk JWT and syncing user data.
    """
    user = await sync_user(auth_payload)
    return {"message": "Login successful", "user": user}

@auth_router.get("/admin-only", response_model=LoginResponse, tags=["Authentication"])
async def admin_only_route(user: dict = Depends(require_role("org:admin:full"))):
    """
    Example API route restricted to Admins.
    """
    return {"message": "Welcome, Admin!", "user": user}

@auth_router.post("/generate-api-key", tags=["Authentication"])
async def generate_api_key(user: dict = Depends(get_current_user)):
    """
    Generates a new API key for the authenticated user.
    """
    return await APIKeyService.generate_api_key(user["user_id"])

@auth_router.get("/validate-api-key", tags=["Authentication"])
async def validate_api_key(user: dict = Depends(verify_api_key)):
    """
    Validates an API key and returns the associated user.
    """
    return {"message": "API Key is valid", "user_id": user["user_id"]}