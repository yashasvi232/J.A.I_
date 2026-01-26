"""
Meeting models for database storage and API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class MeetingProvider(str, Enum):
    GOOGLE_MEET = "google_meet"
    ZOOM = "zoom"

class MeetingType(str, Enum):
    ONLINE = "online"
    IN_PERSON = "in-person"
    PHONE = "phone"

class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MeetingConfigBase(BaseModel):
    """Base meeting configuration"""
    provider: MeetingProvider
    default_duration: int = 60
    buffer_time_minutes: int = 15
    enable_waiting_room: bool = True
    require_password: bool = False

class GoogleMeetCredentials(BaseModel):
    """Google Meet API credentials"""
    client_id: str
    client_secret: str
    refresh_token: str

class ZoomCredentials(BaseModel):
    """Zoom API credentials"""
    api_key: str
    api_secret: str
    account_id: str

class MeetingConfigInDB(MeetingConfigBase):
    """Meeting configuration stored in database"""
    id: str = Field(alias="_id")
    google_credentials: Optional[GoogleMeetCredentials] = None
    zoom_credentials: Optional[ZoomCredentials] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class MeetingConfigCreate(BaseModel):
    """Request to create/update meeting configuration"""
    provider: MeetingProvider
    default_duration: Optional[int] = 60
    buffer_time_minutes: Optional[int] = 15
    enable_waiting_room: Optional[bool] = True
    require_password: Optional[bool] = False
    google_credentials: Optional[GoogleMeetCredentials] = None
    zoom_credentials: Optional[ZoomCredentials] = None

class MeetingConfigResponse(BaseModel):
    """Meeting configuration response"""
    provider: MeetingProvider
    default_duration: int
    buffer_time_minutes: int
    enable_waiting_room: bool
    require_password: bool
    has_google_credentials: bool
    has_zoom_credentials: bool
    updated_at: datetime