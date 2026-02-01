from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.get("/recommendations")
async def get_ai_recommendations(current_user: dict = Depends(get_current_user)):
    """Get AI recommendations - placeholder"""
    return {"recommended_lawyers": []}