from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
import logging

from models.user import UserInDB
from routers.auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_user_cases(current_user: UserInDB = Depends(get_current_user)):
    """Get cases for current user"""
    try:
        logger.info(f"Getting cases for user: {current_user.email} (type: {current_user.user_type}, id: {current_user.id})")
        
        db = get_database()
        
        if current_user.user_type == "client":
            logger.info(f"Searching for client cases with client_id: {current_user.id}")
            cases = await db.cases.find({"client_id": ObjectId(current_user.id)}).to_list(length=100)
        elif current_user.user_type == "lawyer":
            logger.info(f"Searching for lawyer cases with lawyer_id: {current_user.id}")
            cases = await db.cases.find({"lawyer_id": ObjectId(current_user.id)}).to_list(length=100)
        else:
            logger.warning(f"Unknown user type: {current_user.user_type}")
            cases = []
        
        logger.info(f"Found {len(cases)} cases")
        
        # Convert ObjectId to string for JSON serialization
        for case in cases:
            case["_id"] = str(case["_id"])
            if case.get("client_id"):
                case["client_id"] = str(case["client_id"])
            if case.get("lawyer_id"):
                case["lawyer_id"] = str(case["lawyer_id"])
            if case.get("request_id"):
                case["request_id"] = str(case["request_id"])
        
        logger.info(f"Successfully returning {len(cases)} cases")
        return {"cases": cases}
        
    except Exception as e:
        logger.error(f"Error getting cases for user {current_user.email}: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"User ID: {current_user.id}, Type: {type(current_user.id)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cases: {str(e)}"
        )

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
    
    # Convert ObjectId to string for JSON serialization
    if created_case:
        created_case["_id"] = str(created_case["_id"])
        created_case["client_id"] = str(created_case["client_id"])
        if created_case.get("lawyer_id"):
            created_case["lawyer_id"] = str(created_case["lawyer_id"])
        if created_case.get("request_id"):
            created_case["request_id"] = str(created_case["request_id"])
    
    return {"case": created_case}