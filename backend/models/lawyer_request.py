from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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

class RequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class LawyerRequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: str = Field(..., min_length=1, max_length=100)
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    preferred_meeting_type: Optional[str] = Field(None, max_length=50)  # "online", "in-person", "phone"
    location: Optional[str] = Field(None, max_length=200)
    additional_notes: Optional[str] = Field(None, max_length=1000)

class LawyerRequestCreate(LawyerRequestBase):
    lawyer_id: str  # The lawyer being requested

class LawyerRequestInDB(LawyerRequestBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: PyObjectId
    lawyer_id: PyObjectId
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    response_message: Optional[str] = None  # Lawyer's response when accepting/rejecting
    responded_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LawyerRequestResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    urgency_level: UrgencyLevel
    budget_min: Optional[float]
    budget_max: Optional[float]
    preferred_meeting_type: Optional[str]
    location: Optional[str]
    additional_notes: Optional[str]
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    response_message: Optional[str]
    responded_at: Optional[datetime]
    
    # Client information
    client_name: str
    client_email: str
    
    # Lawyer information (for client view)
    lawyer_name: Optional[str] = None
    lawyer_email: Optional[str] = None

class RequestActionRequest(BaseModel):
    action: str  # "accept" or "reject"
    response_message: Optional[str] = Field(None, max_length=500)

class RequestUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    urgency_level: Optional[UrgencyLevel] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    preferred_meeting_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)
    additional_notes: Optional[str] = Field(None, max_length=1000)