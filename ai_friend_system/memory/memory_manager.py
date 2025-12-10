import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database import DatabaseManager, MemoryModel
from config.constants import MemoryTier
from .memory_tiers import MemoryTierManager
from .memory_optimizer import MemoryOptimizer
from concurrent.futures import ThreadPoolExecutor

class MemoryManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.tier_manager = MemoryTierManager()
        self.optimizer = MemoryOptimizer(db_manager)
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def store_memory(self, session: AsyncSession, conversation_id: int, content: str, 
                          context: Dict, importance: float) -> int:
        tier = self.tier_manager.determine_tier(content, importance, context)
        expires_at = self.tier_manager.calculate_expiry(tier)
        
        tags = self._extract_tags(content, context)
        
        memory = MemoryModel(
            id=None,
            conversation_id=conversation_id,
            tier=tier.value,
            content=content,
            context=str(context),
            tags=','.join(tags),
            created_at=datetime.now(),
            expires_at=expires_at,
            importance=importance,
            last_accessed=datetime.now()
        )
        
        memory_id = await self.db_manager.save_memory(session, memory)
        
        # Run optimization in background
        asyncio.create_task(self.optimizer.optimize_memories(session, conversation_id))
        
        return memory_id
    
    async def retrieve_context(self, session: AsyncSession, conversation_id: int, query: str) -> List[Dict]:
        context_memories = []
        
        # Retrieve from different tiers in parallel
        tasks = [
            self.db_manager.get_memories_by_tier(session, conversation_id, MemoryTier.PERMANENT.value),
            self.db_manager.get_memories_by_tier(session, conversation_id, MemoryTier.PERSONAL.value),
            self.db_manager.get_memories_by_tier(session, conversation_id, MemoryTier.TEMPORARY.value)
        ]
        
        results = await asyncio.gather(*tasks)
        
        for memories in results:
            for mem in memories[:5]:  # Limit per tier
                context_memories.append({
                    'content': mem.content,
                    'tier': mem.tier,
                    'importance': mem.importance,
                    'created_at': mem.created_at
                })
                await self.db_manager.update_memory_access(session, mem.id)
        
        return context_memories
    
    def _extract_tags(self, content: str, context: Dict) -> List[str]:
        tags = []
        words = content.lower().split()
        
        # Simple tag extraction
        important_words = [w for w in words if len(w) > 5][:5]
        tags.extend(important_words)
        
        if context.get('emotion'):
            tags.append(f"emotion:{context['emotion']}")
        
        return tags