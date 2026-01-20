from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId
from models.user import PyObjectId

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class CaseStatus(str, Enum):
    OPEN = "open"
    MATCHED = "matched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CaseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    category: str
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    status: Optional[CaseStatus] = None

class CaseInDB(CaseBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    case_number: str
    client_id: PyObjectId
    lawyer_id: Optional[PyObjectId] = None
    status: CaseStatus = CaseStatus.OPEN
    ai_analysis: Optional[Dict[str, Any]] = None
    matching_criteria: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CaseResponse(BaseModel):
    id: str = Field(alias="_id")
    case_number: str
    client_id: str
    lawyer_id: Optional[str] = None
    title: str
    description: str
    category: str
    urgency_level: UrgencyLevel
    budget_min: Optional[float]
    budget_max: Optional[float]
    status: CaseStatus
    ai_analysis: Optional[Dict[str, Any]]
    matching_criteria: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        populate_by_name = True

class AIMatch(BaseModel):
    case_id: PyObjectId
    lawyer_id: PyObjectId
    match_score: float = Field(..., ge=0, le=100)
    match_reasons: Dict[str, Any]
    specialization_match: float = Field(..., ge=0, le=100)
    experience_match: float = Field(..., ge=0, le=100)
    budget_match: float = Field(..., ge=0, le=100)
    availability_match: float = Field(..., ge=0, le=100)
    is_recommended: bool = False

class AIMatchInDB(AIMatch):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AIMatchResponse(BaseModel):
    id: str = Field(alias="_id")
    case_id: str
    lawyer_id: str
    match_score: float
    match_reasons: Dict[str, Any]
    specialization_match: float
    experience_match: float
    budget_match: float
    availability_match: float
    is_recommended: bool
    created_at: datetime

    class Config:
        populate_by_name = True

class CaseSearchFilters(BaseModel):
    status: Optional[CaseStatus] = None
    category: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None
    client_id: Optional[str] = None
    lawyer_id: Optional[str] = None