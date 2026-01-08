from typing import Dict, Any, List, Optional
from datetime import datetime
from agents import AgentCoordinator
from memory import MemoryManager
from .nlp_engine import NLPEngine
from database import DatabaseManager, MessageModel
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import Logger
from config.constants import MessageType
import asyncio

class MessageProcessor:
    def __init__(self, db_manager: DatabaseManager, memory_manager: MemoryManager):
        self.db_manager = db_manager
        self.memory_manager = memory_manager
        self.agent_coordinator = AgentCoordinator()
        self.nlp_engine = NLPEngine()
        self.logger = Logger("MessageProcessor")
    
    # async def process_message(self, session: AsyncSession, conversation_id: int, 
    #                          user_message: str) -> Dict[str, Any]:
    #     start_time = datetime.now()
        
    #     # Clean and analyze text
    #     cleaned_text = self.nlp_engine.clean_text(user_message)
    #     text_analysis = self.nlp_engine.analyze_text(cleaned_text)
        
    #     # Get recent history
    #     recent_messages = await self.db_manager.get_recent_messages(session, conversation_id, limit=5)
    #     history = [{'role': msg.role, 'content': msg.content} for msg in reversed(recent_messages)]
        
    #     # Process with agents in parallel
    #     agent_input = {
    #         'text': cleaned_text,
    #         'history': history,
    #         'analysis': text_analysis
    #     }
    async def process_message(self, session: AsyncSession, conversation_id: int, 
                            user_message: str) -> Dict[str, Any]:
        start_time = datetime.now()
        
        # Optimized: Run text cleaning and history retrieval in parallel
        cleaned_text_task = asyncio.create_task(
            asyncio.to_thread(self.nlp_engine.clean_text, user_message)
        )
        history_task = self.db_manager.get_recent_messages(session, conversation_id, limit=3)  # Reduced from 5
        
        # Wait for both
        cleaned_text, recent_messages = await asyncio.gather(
            cleaned_text_task,
            history_task
        )
        
        # Quick text analysis (lightweight)
        text_analysis = self.nlp_engine.analyze_text(cleaned_text)
        history = [{'role': msg.role, 'content': msg.content} for msg in reversed(recent_messages)]
        
        # Build agent input
        agent_input = {
            'text': cleaned_text,
            'history': history,
            'analysis': text_analysis
        }

        # RUN AGENTS (already optimized with timeouts)
        agent_results = await self.agent_coordinator.process_parallel(agent_input)

        # FIX: return a full dictionary (previously missing → caused NoneType)
# SAFETY GUARD
        if not isinstance(agent_results, dict):
            agent_results = {}

        return {
            "cleaned_text": cleaned_text,
            "analysis": text_analysis,
            "history": history,

            # REQUIRED BY AIFriend
            "agent_results": agent_results,
            "memories": agent_results.get("memories", []),

            "success": agent_results.get("success", True)
        }

