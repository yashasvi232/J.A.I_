from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime

from models.user import UserInDB
from routers.auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter()

@router.post("/match-lawyers")
async def match_lawyers_to_case(
    case_data: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """AI-powered lawyer matching for a case"""
    db = get_database()
    
    # Simple matching algorithm (can be enhanced with actual AI)
    category = case_data.get("category", "")
    location = case_data.get("location", "")
    
    # Find lawyers with matching specializations
    query = {}
    if category:
        query["specializations"] = {"$regex": category, "$options": "i"}
    
    lawyers = await db.lawyers.find(query).limit(10).to_list(length=10)
    
    # Add match scores (simplified)
    for lawyer in lawyers:
        lawyer["match_score"] = 85.0  # Placeholder score
    
    return {"matched_lawyers": lawyers}

@router.get("/recommendations")
async def get_lawyer_recommendations(current_user: UserInDB = Depends(get_current_user)):
    """Get AI-powered lawyer recommendations"""
    db = get_database()
    
    # Get top-rated lawyers
    lawyers = await db.lawyers.find().sort("rating", -1).limit(5).to_list(length=5)
    
    return {"recommended_lawyers": lawyers}