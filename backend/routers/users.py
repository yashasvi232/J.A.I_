from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    return current_user

@router.put("/profile")
async def update_user_profile(profile_data: dict, current_user: dict = Depends(get_current_user)):
    """Update user profile"""
    # TODO: Implement profile update logic
    return {"message": "Profile updated successfully"}