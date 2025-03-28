import httpx
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from app.core.config import settings
from app.api.v1.auth.rbac import ROLE_PERMISSIONS, UserRole
from app.core.database import MongoDB
from typing import Callable
from app.api.v1.auth.services import sync_user
from app.api.v1.auth.apikeys import APIKeyService

# Initialize Clerk SDK
clerk_sdk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

# Security Token Scheme
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Middleware to authenticate API requests using Clerk JWT.
    """
    try:
        # Create a mock request for Clerk validation
        request = httpx.Request(method="GET", url="/")
        request.headers["Authorization"] = f"Bearer {credentials.credentials}"

        # Authenticate request with Clerk
        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(authorized_parties=['https://localhost:3000', 'https://127.0.0.1:3000'])  # Dev Mode
        )

        # If authentication fails, return an error
        if not request_state.is_signed_in:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {request_state.reason}")

        # Return payload containing user info from Clerk
        return request_state.payload

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_current_user(auth_payload: dict = Depends(verify_token)):
    """
    Retrieves the current user from MongoDB and updates their data.
    """
     # Update the user data in the database
    await sync_user(auth_payload)

    db = MongoDB.get_db()
    user = await db.users.find_one({"user_id": auth_payload["sub"]})
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found in database")

    return user

def require_role(required_role: str) -> Callable:
    """
    Middleware function to enforce role-based access control.
    Returns a function that FastAPI can properly await.
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        """
        Checks if the user has the required role.
        """
        user_role = user.get("organizations", [{}])[0].get("org_role")

        if user_role not in ROLE_PERMISSIONS:
            raise HTTPException(status_code=403, detail="Invalid role")

        if required_role not in ROLE_PERMISSIONS[user_role]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # Ensure the returned user matches the expected schema
        return {
            "user_id": user.get("user_id"),
            "email": user.get("email"),
            "full_name": user.get("full_name"),
            "organizations": user.get("organizations"),
            "session_id": user.get("session_id"),
        }

    return role_checker

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Middleware to authenticate external services using API keys.
    """
    if not api_key:
        raise HTTPException(status_code=403, detail="API Key is missing")

    user_id = await APIKeyService.verify_api_key(api_key)
    return {"user_id": user_id}