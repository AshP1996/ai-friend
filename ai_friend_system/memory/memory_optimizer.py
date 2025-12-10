import asyncio
from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database import DatabaseManager, Memory

class MemoryOptimizer:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.optimization_running = False
    
    async def optimize_memories(self, session: AsyncSession, conversation_id: int):
        if self.optimization_running:
            return
        
        self.optimization_running = True
        try:
            await self._cleanup_expired(session)
            await self._consolidate_similar(session, conversation_id)
            await self._update_importance_scores(session, conversation_id)
        finally:
            self.optimization_running = False
    
    async def _cleanup_expired(self, session: AsyncSession):
        await self.db_manager.cleanup_expired_memories(session)
    
    async def _consolidate_similar(self, session: AsyncSession, conversation_id: int):
        # Placeholder for future similarity detection and consolidation
        pass
    
    async def _update_importance_scores(self, session: AsyncSession, conversation_id: int):
        # Update importance based on access patterns
        pass
    
    def calculate_importance(self, content: str, context: Dict, metadata: Dict) -> float:
        importance = 0.5
        
        keywords = ['important', 'remember', 'never forget', 'critical', 'essential']
        if any(kw in content.lower() for kw in keywords):
            importance += 0.2
        
        if context.get('emotion') in ['happy', 'sad', 'excited']:
            importance += 0.1
        
        if metadata.get('user_emphasized', False):
            importance += 0.15
        
        return min(importance, 1.0)