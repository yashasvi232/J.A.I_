from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime

from models.user import UserResponse, UserUpdate, UserInDB
from routers.auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(**current_user.dict())

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update user profile"""
    db = get_database()
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"_id": ObjectId(current_user.id)})
    return UserResponse(**updated_user)

@router.delete("/profile")
async def delete_user_account(current_user: UserInDB = Depends(get_current_user)):
    """Delete user account"""
    db = get_database()
    
    # Soft delete - mark as inactive
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Account deactivated successfully"}