from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import *
from .models import *
from config.constants import MemoryTier
from config import settings
import asyncio
import json

class DatabaseManager:
    def __init__(self):
        self.config = settings.memory_config
    
    async def create_conversation(self, session: AsyncSession, user_id: str, session_id: str) -> int:
        conv = Conversation(
            user_id=user_id, 
            session_id=session_id,
            total_messages=0,
            avg_response_time=0.0,
            conversation_quality=0.5
        )
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
        return conv.id
    
    async def update_conversation_stats(self, session: AsyncSession, conversation_id: int):
        """Update conversation statistics"""
        from sqlalchemy import func
        
        # Get message stats
        msg_stats = await session.execute(
            select(
                func.count(Message.id).label("count"),
                func.avg(Message.processing_time).label("avg_time"),
                func.avg(Message.confidence).label("avg_emotion")
            ).where(Message.conversation_id == conversation_id)
        )
        stats = msg_stats.first()
        
        if stats:
            await session.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(
                    total_messages=stats.count or 0,
                    avg_response_time=stats.avg_time or 0.0,
                    avg_emotion_score=stats.avg_emotion or 0.0,
                    last_active=datetime.utcnow()
                )
            )
            await session.commit()
    
    async def save_message(self, session: AsyncSession, msg: MessageModel) -> int:
        db_msg = Message(
            conversation_id=msg.conversation_id,
            role=msg.role.value if hasattr(msg.role, "value") else msg.role,
            content=msg.content,
            emotion=msg.emotion.value if hasattr(msg.emotion, "value") else msg.emotion,
            confidence=msg.confidence,
            model=msg.model_used,
            tokens_used=msg.tokens_used,
            processing_time=msg.processing_time,
            timestamp=msg.timestamp,
            # Training data fields
            context_embedding=msg.context_embedding,
            agent_outputs=msg.agent_outputs,
            memory_context=msg.memory_context,
            user_feedback=msg.user_feedback,
            quality_score=msg.quality_score,
            training_flag=msg.training_flag,
            # Voice fields
            voice_pitch=msg.voice_pitch,
            voice_emotion=msg.voice_emotion,
            audio_quality=msg.audio_quality,
        )

        session.add(db_msg)
        await session.commit()
        await session.refresh(db_msg)

        return db_msg.id


    
    async def save_memory(self, session: AsyncSession, mem: MemoryModel) -> int:
        db_mem = Memory(
            conversation_id=mem.conversation_id,
            tier=mem.tier.value if hasattr(mem.tier, "value") else mem.tier,
            content=mem.content,
            source=mem.source,
            embedding=mem.embedding,
            importance=mem.importance,
            confidence=mem.confidence,
            context=mem.context,
            tags=mem.tags,
            emotion_at_creation=mem.emotion_at_creation,
            related_memories=mem.related_memories,
            training_relevance=mem.training_relevance,
            verified=mem.verified,
            access_count=mem.access_count,
            created_at=mem.created_at,
            last_accessed=mem.last_accessed,
            expires_at=mem.expires_at,
        )

        session.add(db_mem)
        await session.commit()
        await session.refresh(db_mem)

        return db_mem.id


    
    async def get_recent_messages(self, session: AsyncSession, conversation_id: int, limit: int = 10) -> List[Message]:
        # Optimized: Only select needed columns and use index
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())  # Convert to list for faster iteration
    
    async def get_memories_by_tier(self, session: AsyncSession, conversation_id: int, tier: str) -> List[Memory]:
        # Optimized: Limit results and use index
        result = await session.execute(
            select(Memory)
            .where(Memory.conversation_id == conversation_id, Memory.tier == tier)
            .order_by(Memory.importance.desc(), Memory.last_accessed.desc())
            .limit(5)  # Limit for speed
        )
        return list(result.scalars().all())
    
    async def cleanup_expired_memories(self, session: AsyncSession):
        now = datetime.now()
        await session.execute(
            delete(Memory).where(Memory.expires_at <= now, Memory.expires_at.isnot(None))
        )
        await session.commit()
    
    async def update_memory_access(self, session: AsyncSession, memory_id: int):
        await session.execute(
            update(Memory)
            .where(Memory.id == memory_id)
            .values(access_count=Memory.access_count + 1, last_accessed=datetime.now())
        )
        await session.commit()
    
    async def get_user_profile(self, session: AsyncSession, user_id: str) -> Optional[UserProfile]:
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def save_personal_info(self, session: AsyncSession, user_id: str, category: str, key: str, value: str):
        info = PersonalInfo(user_id=user_id, category=category, key=key, value=value)
        session.add(info)
        await session.commit()
    
    async def get_persona(self, session: AsyncSession, user_id: str) -> Optional[PersonaModel]:
        """Get persona configuration for a user"""
        result = await session.execute(
            select(Persona).where(Persona.user_id == user_id)
        )
        db_persona = result.scalar_one_or_none()
        
        if not db_persona:
            return None
        
        # Deserialize JSON fields
        personality_traits = {}
        interests = []
        
        if db_persona.personality_traits:
            try:
                personality_traits = json.loads(db_persona.personality_traits)
            except (json.JSONDecodeError, TypeError):
                personality_traits = {}
        
        if db_persona.interests:
            try:
                interests = json.loads(db_persona.interests)
            except (json.JSONDecodeError, TypeError):
                interests = []
        
        return PersonaModel(
            id=db_persona.id,
            user_id=db_persona.user_id,
            name=db_persona.name,
            personality_traits=personality_traits,
            speaking_style=db_persona.speaking_style,
            interests=interests,
            background_story=db_persona.background_story,
            voice_id=db_persona.voice_id,
            created_at=db_persona.created_at,
            updated_at=db_persona.updated_at
        )
    
    async def save_persona(self, session: AsyncSession, persona: PersonaModel) -> int:
        """Save or update persona configuration"""
        # Check if persona exists
        result = await session.execute(
            select(Persona).where(Persona.user_id == persona.user_id)
        )
        db_persona = result.scalar_one_or_none()
        
        # Serialize JSON fields
        personality_traits_json = json.dumps(persona.personality_traits) if persona.personality_traits else None
        interests_json = json.dumps(persona.interests) if persona.interests else None
        
        if db_persona:
            # Update existing
            db_persona.name = persona.name
            db_persona.personality_traits = personality_traits_json
            db_persona.speaking_style = persona.speaking_style
            db_persona.interests = interests_json
            db_persona.background_story = persona.background_story
            db_persona.voice_id = persona.voice_id
            db_persona.updated_at = datetime.utcnow()
        else:
            # Create new
            db_persona = Persona(
                user_id=persona.user_id,
                name=persona.name,
                personality_traits=personality_traits_json,
                speaking_style=persona.speaking_style,
                interests=interests_json,
                background_story=persona.background_story,
                voice_id=persona.voice_id
            )
            session.add(db_persona)
        
        await session.commit()
        await session.refresh(db_persona)
        return db_persona.id
    
    async def delete_persona(self, session: AsyncSession, user_id: str):
        """Delete persona configuration for a user"""
        await session.execute(
            delete(Persona).where(Persona.user_id == user_id)
        )
        await session.commit()