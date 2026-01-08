import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database import DatabaseManager, MemoryModel
from config.constants import MemoryTier
from .memory_tiers import MemoryTierManager
from .memory_optimizer import MemoryOptimizer
from .semantic_scorer import SemanticScorer
from concurrent.futures import ThreadPoolExecutor

class MemoryManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.tier_manager = MemoryTierManager()
        self.optimizer = MemoryOptimizer(db_manager)
        self.semantic_scorer = SemanticScorer()  # Advanced: semantic relevance scoring
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def store_memory(self, session: AsyncSession, conversation_id: int, content: str, 
                          context: Dict, importance: float) -> int:
        tier = self.tier_manager.determine_tier(content, importance, context)
        expires_at = self.tier_manager.calculate_expiry(tier)
        
        tags = self._extract_tags(content, context)
        
        # Extract emotion from context if available
        emotion_at_creation = None
        if isinstance(context, dict):
            emotion_data = context.get("emotion", {})
            if isinstance(emotion_data, dict):
                emotion_at_creation = emotion_data.get("emotion", "neutral")
            elif isinstance(emotion_data, str):
                emotion_at_creation = emotion_data
        
        memory = MemoryModel(
            id=None,
            conversation_id=conversation_id,
            tier=tier.value,
            content=content,
            context=str(context) if context else None,
            tags=','.join(tags) if tags else None,
            emotion_at_creation=emotion_at_creation,
            created_at=datetime.now(),
            expires_at=expires_at,
            importance=importance,
            last_accessed=datetime.now(),
            training_relevance=importance  # Use importance as training relevance
        )
        
        memory_id = await self.db_manager.save_memory(session, memory)
        
        # Run optimization in background
        asyncio.create_task(self.optimizer.optimize_memories(session, conversation_id))
        
        return memory_id
    
    async def retrieve_context(self, session: AsyncSession, conversation_id: int, 
                              query: str, conversation_context: Dict[str, Any] = None) -> List[Dict]:
        """ADVANCED: Optimized memory retrieval with semantic relevance scoring"""
        context_memories = []
        
        # Retrieve from different tiers in parallel with strict limits
        tasks = [
            self.db_manager.get_memories_by_tier(session, conversation_id, MemoryTier.PERMANENT.value),
            self.db_manager.get_memories_by_tier(session, conversation_id, MemoryTier.PERSONAL.value),
            self.db_manager.get_memories_by_tier(session, conversation_id, MemoryTier.TEMPORARY.value)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Convert to dict format for scoring
        all_memories = []
        for memories in results:
            for mem in memories:
                all_memories.append({
                    'content': mem.content,
                    'tier': mem.tier,
                    'importance': mem.importance,
                    'created_at': mem.created_at,
                    'last_accessed': mem.last_accessed,
                    'tags': mem.tags,
                    'emotion_at_creation': mem.emotion_at_creation,
                    'id': mem.id
                })
        
        # ADVANCED: Rank memories by semantic relevance
        if all_memories:
            scored_memories = self.semantic_scorer.rank_memories(
                all_memories, 
                query, 
                conversation_context
            )
            
            # Take top 5 most relevant
            top_memories = scored_memories[:5]
            
            for mem in top_memories:
                context_memories.append({
                    'content': mem['content'],
                    'tier': mem['tier'],
                    'importance': mem['importance'],
                    'created_at': mem['created_at'],
                    'relevance_score': mem.get('relevance_score', 0.0)  # Add relevance score
                })
            
            # Batch update memory access for retrieved memories
            memory_ids_to_update = [mem['id'] for mem in top_memories]
            if memory_ids_to_update:
                asyncio.create_task(self._batch_update_memory_access(session, memory_ids_to_update))
        
        return context_memories
    
    async def _batch_update_memory_access(self, session: AsyncSession, memory_ids: List[int]):
        """Batch update memory access counts for performance"""
        try:
            from sqlalchemy import update
            from database.schema import Memory
            from datetime import datetime
            
            await session.execute(
                update(Memory)
                .where(Memory.id.in_(memory_ids))
                .values(
                    access_count=Memory.access_count + 1,
                    last_accessed=datetime.utcnow()
                )
            )
            await session.commit()
        except Exception:
            pass  # Non-critical, can fail silently
    
    def _extract_tags(self, content: str, context: Dict) -> List[str]:
        tags = []
        words = content.lower().split()
        
        # Simple tag extraction
        important_words = [w for w in words if len(w) > 5][:5]
        tags.extend(important_words)
        
        if context.get('emotion'):
            tags.append(f"emotion:{context['emotion']}")
        
        return tags