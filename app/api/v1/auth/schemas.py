from pydantic import BaseModel, EmailStr
from typing import Optional, List

class OrganizationModel(BaseModel):
    org_id: str
    org_name: str
    org_slug: str
    org_role: str
    org_image_url: str
    org_permissions: List[str]

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    profile_pic: Optional[str] = None
    organizations: List[OrganizationModel]
    session_id: str
    model_config = {
        "from_attributes": True
    }

class LoginResponse(BaseModel):
    message: str
    user: UserResponse