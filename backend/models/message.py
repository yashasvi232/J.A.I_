from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"
    MEETING_UPDATE = "meeting_update"
    SYSTEM = "system"

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.TEXT
    file_url: Optional[str] = None
    file_name: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    request_id: PyObjectId  # Links to the lawyer request
    sender_id: PyObjectId   # User who sent the message
    sender_type: str        # "client" or "lawyer"
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MessageResponse(BaseModel):
    id: str
    request_id: str
    sender_id: str
    sender_type: str
    sender_name: str  # Full name of sender
    content: str
    message_type: MessageType
    file_url: Optional[str]
    file_name: Optional[str]
    is_read: bool
    created_at: datetime
    updated_at: datetime

class ConversationResponse(BaseModel):
    request_id: str
    request_title: str
    client_name: str
    lawyer_name: str
    status: str
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    messages: List[MessageResponse] = []
    created_at: datetime
    updated_at: datetime

class MarkAsReadRequest(BaseModel):
    message_ids: List[str]