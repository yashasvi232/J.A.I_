from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime

from models.lawyer import (
    LawyerProfileCreate, LawyerProfileUpdate, LawyerResponse, 
    LawyerInDB, LawyerSearchFilters, AvailabilityStatus
)
from models.user import UserInDB, UserType
from routers.auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter()

@router.post("/profile", response_model=LawyerResponse)
async def create_lawyer_profile(
    lawyer_data: LawyerProfileCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create lawyer profile"""
    if current_user.user_type != UserType.LAWYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can create lawyer profiles"
        )
    
    db = get_database()
    
    # Check if lawyer profile already exists
    existing_profile = await db.lawyers.find_one({"user_id": ObjectId(current_user.id)})
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lawyer profile already exists"
        )
    
    # Check if bar number is unique
    existing_bar = await db.lawyers.find_one({"bar_number": lawyer_data.bar_number})
    if existing_bar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bar number already registered"
        )
    
    # Create lawyer profile
    lawyer_dict = lawyer_data.dict()
    lawyer_dict["user_id"] = ObjectId(current_user.id)
    lawyer_dict["created_at"] = datetime.utcnow()
    lawyer_dict["updated_at"] = datetime.utcnow()
    
    result = await db.lawyers.insert_one(lawyer_dict)
    created_lawyer = await db.lawyers.find_one({"_id": result.inserted_id})
    
    return LawyerResponse(**created_lawyer)

@router.get("/profile", response_model=LawyerResponse)
async def get_lawyer_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current lawyer's profile"""
    if current_user.user_type != UserType.LAWYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can access lawyer profiles"
        )
    
    db = get_database()
    lawyer_profile = await db.lawyers.find_one({"user_id": ObjectId(current_user.id)})
    
    if not lawyer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )
    
    return LawyerResponse(**lawyer_profile)

@router.put("/profile", response_model=LawyerResponse)
async def update_lawyer_profile(
    lawyer_update: LawyerProfileUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update lawyer profile"""
    if current_user.user_type != UserType.LAWYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can update lawyer profiles"
        )
    
    db = get_database()
    
    update_data = {k: v for k, v in lawyer_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.lawyers.update_one(
        {"user_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer profile not found"
        )
    
    updated_lawyer = await db.lawyers.find_one({"user_id": ObjectId(current_user.id)})
    return LawyerResponse(**updated_lawyer)

@router.get("/search", response_model=List[LawyerResponse])
async def search_lawyers(
    specializations: Optional[List[str]] = Query(None),
    min_experience: Optional[int] = Query(None),
    max_hourly_rate: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None),
    languages: Optional[List[str]] = Query(None),
    availability_status: Optional[AvailabilityStatus] = Query(None),
    bar_state: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    skip: int = Query(0, ge=0)
):
    """Search lawyers with filters"""
    db = get_database()
    
    # Build query
    query = {}
    
    if specializations:
        query["specializations"] = {"$in": specializations}
    
    if min_experience is not None:
        query["years_experience"] = {"$gte": min_experience}
    
    if max_hourly_rate is not None:
        query["hourly_rate"] = {"$lte": max_hourly_rate}
    
    if min_rating is not None:
        query["rating"] = {"$gte": min_rating}
    
    if languages:
        query["languages"] = {"$in": languages}
    
    if availability_status:
        query["availability_status"] = availability_status
    
    if bar_state:
        query["bar_state"] = bar_state
    
    # Execute query
    cursor = db.lawyers.find(query).skip(skip).limit(limit).sort("rating", -1)
    lawyers = await cursor.to_list(length=limit)
    
    return [LawyerResponse(**lawyer) for lawyer in lawyers]

@router.get("/{lawyer_id}", response_model=LawyerResponse)
async def get_lawyer_by_id(lawyer_id: str):
    """Get lawyer profile by ID"""
    db = get_database()
    
    if not ObjectId.is_valid(lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid lawyer ID"
        )
    
    lawyer = await db.lawyers.find_one({"_id": ObjectId(lawyer_id)})
    
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    
    return LawyerResponse(**lawyer)