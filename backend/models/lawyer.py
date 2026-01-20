from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from bson import ObjectId
from models.user import PyObjectId

class Education(BaseModel):
    school: str
    degree: str
    year: int
    description: Optional[str] = None

class Certification(BaseModel):
    name: str
    issuer: str
    year: int
    expiry_year: Optional[int] = None

class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"

class LawyerProfile(BaseModel):
    user_id: PyObjectId
    bar_number: str = Field(..., min_length=1)
    bar_state: str = Field(..., min_length=2, max_length=50)
    law_firm: Optional[str] = None
    years_experience: int = Field(..., ge=0)
    hourly_rate: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    specializations: List[str] = []
    education: List[Education] = []
    certifications: List[Certification] = []
    languages: List[str] = ["English"]
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    rating: float = Field(default=0.0, ge=0, le=5)
    total_reviews: int = Field(default=0, ge=0)
    total_cases: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.0, ge=0, le=100)
    ai_match_score: float = Field(default=0.0, ge=0, le=100)

class LawyerProfileCreate(BaseModel):
    bar_number: str = Field(..., min_length=1)
    bar_state: str = Field(..., min_length=2, max_length=50)
    law_firm: Optional[str] = None
    years_experience: int = Field(..., ge=0)
    hourly_rate: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    specializations: List[str] = []
    education: List[Education] = []
    certifications: List[Certification] = []
    languages: List[str] = ["English"]

class LawyerProfileUpdate(BaseModel):
    law_firm: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    specializations: Optional[List[str]] = None
    education: Optional[List[Education]] = None
    certifications: Optional[List[Certification]] = None
    languages: Optional[List[str]] = None
    availability_status: Optional[AvailabilityStatus] = None

class LawyerInDB(LawyerProfile):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LawyerResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    bar_number: str
    bar_state: str
    law_firm: Optional[str]
    years_experience: int
    hourly_rate: Optional[float]
    bio: Optional[str]
    specializations: List[str]
    education: List[Education]
    certifications: List[Certification]
    languages: List[str]
    availability_status: AvailabilityStatus
    rating: float
    total_reviews: int
    total_cases: int
    success_rate: float
    ai_match_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class LawyerSearchFilters(BaseModel):
    specializations: Optional[List[str]] = None
    min_experience: Optional[int] = None
    max_hourly_rate: Optional[float] = None
    min_rating: Optional[float] = None
    languages: Optional[List[str]] = None
    availability_status: Optional[AvailabilityStatus] = None
    bar_state: Optional[str] = None