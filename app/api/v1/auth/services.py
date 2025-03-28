from datetime import datetime, timezone
from fastapi import HTTPException
from app.api.v1.auth.models import User
from app.core.database import MongoDB

async def sync_user(auth_payload: dict):
    """
    Syncs the authenticated Clerk user with our MongoDB database.
    """
    user_data = User(
        user_id=auth_payload["sub"],
        email=auth_payload["email"],
        full_name=auth_payload.get("fullName"),
        first_name=auth_payload.get("fName"),
        last_name=auth_payload.get("lName"),
        profile_pic=auth_payload.get("profilePic"),
        created_at=datetime.fromtimestamp(auth_payload["iat"], tz=timezone.utc),
        last_sign_in_at=datetime.fromtimestamp(auth_payload["exp"], tz=timezone.utc),
        organizations=[
            {
                "org_id": auth_payload.get("org_id"),
                "org_name": auth_payload.get("orgName"),
                "org_slug": auth_payload.get("org_slug"),
                "org_role": auth_payload.get("org_role"),
                "org_image_url": auth_payload.get("orgImageUrl"),
                "org_permissions": auth_payload.get("org_permissions", []),
            }
        ],
        session_id=auth_payload.get("sid"),
        issuer=auth_payload.get("iss"),
    )

    db = MongoDB.get_db()
    existing_user = await db.users.find_one({"user_id": user_data.user_id})

    if existing_user:
        # Update user data
        await db.users.update_one(
            {"user_id": user_data.user_id},
            {"$set": user_data.model_dump()}
        )
        return {**user_data.model_dump(), "message": "User updated successfully"}

    # Insert new user
    await db.users.insert_one(user_data.model_dump())
    return {**user_data.model_dump(), "message": "New user created"}
