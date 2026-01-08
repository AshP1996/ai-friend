"""
AI Persona customization
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
from .user import get_anonymous_user as get_current_user
from database import DatabaseManager
from database.models import PersonaModel
from config import db_config
from utils.logger import Logger

router = APIRouter()
logger = Logger("PersonaRoute")
db_manager = DatabaseManager()

class PersonaConfig(BaseModel):
    name: str = "Friend"
    personality_traits: Dict[str, float] = {
        "friendliness": 0.9,
        "humor": 0.7,
        "empathy": 0.9,
        "formality": 0.3
    }
    speaking_style: str = "casual"
    interests: List[str] = ["technology", "music", "books"]
    background_story: Optional[str] = None
    voice_id: Optional[str] = None

def persona_model_to_config(persona: PersonaModel) -> PersonaConfig:
    """Convert PersonaModel to PersonaConfig"""
    return PersonaConfig(
        name=persona.name,
        personality_traits=persona.personality_traits,
        speaking_style=persona.speaking_style,
        interests=persona.interests,
        background_story=persona.background_story,
        voice_id=persona.voice_id
    )

def persona_config_to_model(config: PersonaConfig, user_id: str) -> PersonaModel:
    """Convert PersonaConfig to PersonaModel"""
    return PersonaModel(
        id=None,
        user_id=user_id,
        name=config.name,
        personality_traits=config.personality_traits,
        speaking_style=config.speaking_style,
        interests=config.interests,
        background_story=config.background_story,
        voice_id=config.voice_id
    )

@router.get("/get")
async def get_persona(user_id: str = Depends(get_current_user)):
    """Get current persona configuration"""
    try:
        async for session in db_config.get_session():
            persona = await db_manager.get_persona(session, user_id)
            
            if persona:
                return persona_model_to_config(persona)
            else:
                # Return default if no persona exists
                return PersonaConfig()
    except Exception as e:
        logger.error(f"Error getting persona: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get persona: {str(e)}")

@router.post("/update")
async def update_persona(
    config: PersonaConfig,
    user_id: str = Depends(get_current_user)
):
    """Update persona configuration"""
    try:
        persona_model = persona_config_to_model(config, user_id)
        
        async for session in db_config.get_session():
            await db_manager.save_persona(session, persona_model)
        
        logger.info(f"Persona updated for user: {user_id}")
        return {"message": "Persona updated", "config": config}
    except Exception as e:
        logger.error(f"Error updating persona: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update persona: {str(e)}")

@router.post("/reset")
async def reset_persona(user_id: str = Depends(get_current_user)):
    """Reset persona to default"""
    try:
        default_config = PersonaConfig()
        persona_model = persona_config_to_model(default_config, user_id)
        
        async for session in db_config.get_session():
            await db_manager.save_persona(session, persona_model)
        
        logger.info(f"Persona reset for user: {user_id}")
        return {"message": "Persona reset to default", "config": default_config}
    except Exception as e:
        logger.error(f"Error resetting persona: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset persona: {str(e)}")
