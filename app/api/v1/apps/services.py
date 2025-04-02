import secrets
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.database import MongoDB
from app.api.v1.apps.models import AppModel, AppCreateRequest

class AppService:
    @staticmethod
    async def create_app(user_id: str, app_data: AppCreateRequest):
        """
        Creates a new App, generates a unique API key, and stores it.
        """
        db = MongoDB.get_db()

        # Generate a unique App ID and API key
        app_id = secrets.token_hex(16)
        api_key = secrets.token_hex(32)

        app_entry = AppModel(
            app_id=app_id,
            name=app_data.name,
            description=app_data.description,
            domain=app_data.domain,
            category=app_data.category,
            type=app_data.type,
            environment=app_data.environment,
            billing_info=app_data.billing_info,
            tags=app_data.tags,
            region=app_data.region,
            owner_id=user_id,
            api_key=api_key,
            status="Active",
            created_at=datetime.now(timezone.utc),
            created_by=user_id,
        )

        # Store App in MongoDB
        await db.apps.insert_one(app_entry.model_dump())
        return {"message": "App created successfully", "app": app_entry}
    
    @staticmethod
    async def get_app(app_id: str, user_id: str):
        """
        Retrieves an app by its ID, ensuring the user owns it.
        """
        db = MongoDB.get_db()
        app = await db.apps.find_one({"app_id": app_id, "owner_id": user_id})

        if not app:
            raise HTTPException(status_code=404, detail="App not found or unauthorized")

        return app

    @staticmethod
    async def get_user_apps(user_id: str):
        """
        Retrieves all apps owned by the authenticated user.
        """
        db = MongoDB.get_db()
        apps = await db.apps.find({"owner_id": user_id}).to_list(None)

        # Convert ObjectId to string for JSON serialization
        for app in apps:
            app["_id"] = str(app["_id"])  # Convert ObjectId to string

        return {"apps": apps}
