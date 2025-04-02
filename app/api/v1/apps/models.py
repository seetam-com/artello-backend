from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class AppCreateRequest(BaseModel):
    """
    Request model for creating a new app.
    """
    name: str = Field(..., title="App Name", max_length=100)
    description: Optional[str] = Field(None, title="App Description")
    domain: HttpUrl = Field(..., title="Primary Domain")
    category: str = Field(..., title="App Category", max_length=50)
    type: str = Field(..., title="App Type", max_length=50)  # e.g., Web, Mobile, API
    environment: str = Field(..., title="Environment", max_length=50)  # e.g., Development, Production
    billing_info: Optional[str] = Field(None, title="Billing Information")
    tags: List[str] = Field(default_factory=list, title="Tags for Categorization")
    region: str = Field(..., title="Hosting Region")  # e.g., US-East, Europe-West

class AppModel(BaseModel):
    """
    Data model for storing app details.
    """
    app_id: str = Field(..., title="App ID")
    name: str = Field(..., title="App Name")
    description: Optional[str] = Field(None, title="App Description")
    domain: HttpUrl = Field(..., title="Primary Domain")
    category: str = Field(..., title="App Category")
    type: str = Field(..., title="App Type")
    environment: str = Field(..., title="Environment")
    billing_info: Optional[str] = Field(None, title="Billing Information")
    tags: List[str] = Field(default_factory=list, title="Tags for Categorization")
    region: str = Field(..., title="Hosting Region")
    owner_id: str = Field(..., title="Owner User ID")
    api_key: str = Field(..., title="Unique API Key for the App")
    status: str = Field(default="Active", title="App Status")  # Default to Active
    created_at: datetime = Field(default_factory=datetime.now, title="Creation Timestamp")
    created_by: str = Field(..., title="Created By User ID")
