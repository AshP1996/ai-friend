"""
AI Persona customization
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from api.routes.auth import get_current_user

router = APIRouter()

class PersonaConfig(BaseModel):
    name: str = "Friend"
    personality_traits: Dict[str, float] = {
        "friendliness": 0.9,
        "humor": 0.7,
        "empathy": 0.9,
        "formality": 0.3
    }
    speaking_style: str = "casual"
    interests: list = ["technology", "music", "books"]
    background_story: Optional[str] = None
    voice_id: Optional[str] = None

persona_store = {}  # In-memory store (use DB in production)

@router.get("/get")
async def get_persona(user_id: str = Depends(get_current_user)):
    '''Get current persona configuration'''
    return persona_store.get(user_id, PersonaConfig())

@router.post("/update")
async def update_persona(
    config: PersonaConfig,
    user_id: str = Depends(get_current_user)
):
    '''Update persona configuration'''
    persona_store[user_id] = config
    return {"message": "Persona updated", "config": config}

@router.post("/reset")
async def reset_persona(user_id: str = Depends(get_current_user)):
    '''Reset persona to default'''
    default = PersonaConfig()
    persona_store[user_id] = default
    return {"message": "Persona reset to default", "config": default}
