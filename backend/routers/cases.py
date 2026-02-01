from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime

from models.user import UserInDB
from routers.auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def get_user_cases(current_user: UserInDB = Depends(get_current_user)):
    """Get cases for current user"""
    db = get_database()
    
    if current_user.user_type == "client":
        cases = await db.cases.find({"client_id": ObjectId(current_user.id)}).to_list(length=100)
    elif current_user.user_type == "lawyer":
        cases = await db.cases.find({"lawyer_id": ObjectId(current_user.id)}).to_list(length=100)
    else:
        cases = []
    
    return {"cases": cases}

@router.post("/")
async def create_case(case_data: dict, current_user: UserInDB = Depends(get_current_user)):
    """Create a new case"""
    db = get_database()
    
    case_dict = case_data.copy()
    case_dict["client_id"] = ObjectId(current_user.id)
    case_dict["created_at"] = datetime.utcnow()
    case_dict["updated_at"] = datetime.utcnow()
    case_dict["status"] = "open"
    
    result = await db.cases.insert_one(case_dict)
    created_case = await db.cases.find_one({"_id": result.inserted_id})
    
    return {"case": created_case}