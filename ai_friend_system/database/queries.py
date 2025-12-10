from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import *
from typing import List, Dict, Any
from datetime import datetime, timedelta

class Queries:
    @staticmethod
    async def get_conversation_stats(session: AsyncSession, conversation_id: int) -> Dict[str, Any]:
        msg_count = await session.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
        )
        
        avg_processing = await session.execute(
            select(func.avg(Message.processing_time)).where(Message.conversation_id == conversation_id)
        )
        
        return {
            'message_count': msg_count.scalar(),
            'avg_processing_time': avg_processing.scalar() or 0
        }
    
    @staticmethod
    async def search_memories(session: AsyncSession, conversation_id: int, query: str, limit: int = 5) -> List[Memory]:
        result = await session.execute(
            select(Memory)
            .where(
                Memory.conversation_id == conversation_id,
                or_(
                    Memory.content.contains(query),
                    Memory.context.contains(query),
                    Memory.tags.contains(query)
                )
            )
            .order_by(Memory.importance.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_important_memories(session: AsyncSession, conversation_id: int, min_importance: float = 0.7) -> List[Memory]:
        result = await session.execute(
            select(Memory)
            .where(
                Memory.conversation_id == conversation_id,
                Memory.importance >= min_importance
            )
            .order_by(Memory.importance.desc())
        )
        return result.scalars().all()