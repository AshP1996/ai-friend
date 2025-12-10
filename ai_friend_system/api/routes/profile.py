from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils.logger import Logger

router = APIRouter()
logger = Logger("ProfileRoute")

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[str] = None
    interests: Optional[str] = None

@router.get("/{user_id}")
async def get_profile(user_id: str):
    return {"user_id": user_id, "profile": {}}

@router.put("/{user_id}")
async def update_profile(user_id: str, profile: ProfileUpdate):
    return {"message": "Profile updated", "user_id": user_id}