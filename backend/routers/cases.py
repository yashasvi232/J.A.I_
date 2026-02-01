from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_user_cases(current_user: dict = Depends(get_current_user)):
    """Get user cases - placeholder"""
    return {"cases": []}

@router.post("/")
async def create_case(case_data: dict, current_user: dict = Depends(get_current_user)):
    """Create new case - placeholder"""
    return {"message": "Case created successfully"}