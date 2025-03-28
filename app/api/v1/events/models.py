from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional

class EventModel(BaseModel):
    event_id: str = Field(..., title="Event ID")
    session_id: str = Field(..., title="Session ID")
    app_id: str = Field(..., title="App ID")
    event_type: str = Field(..., title="Event Type")
    action: Optional[str] = Field(None, title="Action Type")  # Button Click, Navigation, etc.
    payload: Dict = Field(..., title="Event Payload")
    timestamp: datetime = Field(default_factory=datetime.astimezone, title="Event Timestamp")
