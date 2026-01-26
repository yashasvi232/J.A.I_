from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"
    MEETING_UPDATE = "meeting_update"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: Optional[str] = None
    request_id: str
    sender_id: str
    sender_type: str  # "client" or "lawyer"
    sender_name: str
    message_type: MessageType = MessageType.TEXT
    content: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False
    edited_at: Optional[datetime] = None

class ChatMessageCreate(BaseModel):
    request_id: str
    message_type: MessageType = MessageType.TEXT
    content: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: str
    request_id: str
    sender_id: str
    sender_type: str
    sender_name: str
    message_type: MessageType
    content: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    timestamp: datetime
    is_read: bool
    edited_at: Optional[datetime] = None

class ChatSummary(BaseModel):
    request_id: str
    request_title: str
    client_name: str
    lawyer_name: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0
    total_messages: int = 0