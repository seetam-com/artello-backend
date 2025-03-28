from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
import secrets

class AppCreateRequest(BaseModel):
    name: str = Field(..., title="App Name", max_length=100)
    description: Optional[str] = Field(None, title="App Description")

class AppModel(BaseModel):
    app_id: str = Field(..., title="App ID")
    name: str = Field(..., title="App Name")
    description: Optional[str] = Field(None, title="App Description")
    owner_id: str = Field(..., title="Owner User ID")
    api_key: str = Field(..., title="Unique API Key for the App")
    registered_domains: List[HttpUrl]
    created_at: datetime = Field(default_factory=datetime.astimezone, title="Creation Timestamp")
