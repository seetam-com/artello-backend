from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Organization(BaseModel):
    org_id: str
    org_name: str
    org_slug: str
    org_role: str
    org_image_url: Optional[str] = None
    org_permissions: List[str]

class User(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    first_name: str
    last_name: str
    profile_pic: Optional[str] = None
    created_at: datetime
    last_sign_in_at: datetime
    organizations: List[Organization]
    session_id: str
    issuer: str