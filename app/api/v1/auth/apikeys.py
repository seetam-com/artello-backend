import secrets
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.database import MongoDB

class APIKeyService:
    @staticmethod
    async def generate_api_key(user_id: str):
        """
        Generate a new API key and store it securely.
        """
        api_key = secrets.token_hex(32)  # Secure 256-bit key
        created_at = datetime.now(timezone.utc)

        db = MongoDB.get_db()
        await db.api_keys.insert_one({
            "user_id": user_id,
            "api_key": api_key,
            "created_at": created_at,
        })

        return {"api_key": api_key, "created_at": created_at}

    @staticmethod
    async def verify_api_key(api_key: str):
        """
        Validate an API key and retrieve the associated user.
        """
        db = MongoDB.get_db()
        key_data = await db.api_keys.find_one({"api_key": api_key})

        if not key_data:
            raise HTTPException(status_code=401, detail="Invalid API Key")

        return key_data["user_id"]
