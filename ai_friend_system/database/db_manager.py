from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import *
from .models import *
from config.constants import MemoryTier
from config import settings
import asyncio

class DatabaseManager:
    def __init__(self):
        self.config = settings.memory_config
    
    async def create_conversation(self, session: AsyncSession, user_id: str, session_id: str) -> int:
        conv = Conversation(user_id=user_id, session_id=session_id)
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
        return conv.id
    
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
            created_at=mem.created_at,
            last_accessed=mem.last_accessed,
            expires_at=mem.expires_at,
        )

        session.add(db_mem)
        await session.commit()
        await session.refresh(db_mem)

        return db_mem.id


    
    async def get_recent_messages(self, session: AsyncSession, conversation_id: int, limit: int = 10) -> List[Message]:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_memories_by_tier(self, session: AsyncSession, conversation_id: int, tier: str) -> List[Memory]:
        result = await session.execute(
            select(Memory)
            .where(Memory.conversation_id == conversation_id, Memory.tier == tier)
            .order_by(Memory.importance.desc(), Memory.last_accessed.desc())
        )
        return result.scalars().all()
    
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