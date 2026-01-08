"""
Training data export and management for AI model training
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .schema import Conversation, Message, Memory, AgentLog
from utils.logger import Logger

logger = Logger("TrainingData")

class TrainingDataExporter:
    """Export conversation data for AI model training"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def export_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """Export full conversation with all metadata for training"""
        # Get conversation
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        
        if not conv:
            return None
        
        # Get all messages
        messages_result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
        )
        messages = messages_result.scalars().all()
        
        # Get all memories
        memories_result = await self.session.execute(
            select(Memory)
            .where(Memory.conversation_id == conversation_id)
        )
        memories = memories_result.scalars().all()
        
        # Get agent logs
        agent_logs_result = await self.session.execute(
            select(AgentLog)
            .where(AgentLog.conversation_id == conversation_id)
            .order_by(AgentLog.timestamp)
        )
        agent_logs = agent_logs_result.scalars().all()
        
        # Build training data structure
        training_data = {
            "conversation_id": conv.id,
            "session_id": conv.session_id,
            "user_id": conv.user_id,
            "metadata": {
                "model_used": conv.model_used,
                "language": conv.language,
                "platform": conv.platform,
                "started_at": conv.started_at.isoformat() if conv.started_at else None,
                "ended_at": conv.ended_at.isoformat() if conv.ended_at else None,
                "total_messages": conv.total_messages,
                "avg_response_time": conv.avg_response_time,
                "conversation_quality": conv.conversation_quality,
                "user_satisfaction": conv.user_satisfaction,
                "topics_discussed": json.loads(conv.topics_discussed) if conv.topics_discussed else []
            },
            "messages": [],
            "memories": [],
            "agent_logs": []
        }
        
        # Process messages
        for msg in messages:
            message_data = {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "emotion": msg.emotion,
                "confidence": msg.confidence,
                "model": msg.model,
                "tokens_used": msg.tokens_used,
                "processing_time": msg.processing_time,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "voice_data": {
                    "pitch": msg.voice_pitch,
                    "emotion": msg.voice_emotion,
                    "audio_quality": msg.audio_quality
                } if msg.voice_pitch else None,
                "context": {
                    "embedding": json.loads(msg.context_embedding) if msg.context_embedding else None,
                    "agent_outputs": json.loads(msg.agent_outputs) if msg.agent_outputs else None,
                    "memory_context": json.loads(msg.memory_context) if msg.memory_context else None
                },
                "feedback": {
                    "user_rating": msg.user_feedback,
                    "quality_score": msg.quality_score
                } if msg.user_feedback else None
            }
            training_data["messages"].append(message_data)
        
        # Process memories
        for mem in memories:
            memory_data = {
                "id": mem.id,
                "tier": mem.tier,
                "content": mem.content,
                "source": mem.source,
                "importance": mem.importance,
                "confidence": mem.confidence,
                "context": mem.context,
                "tags": mem.tags.split(",") if mem.tags else [],
                "emotion_at_creation": mem.emotion_at_creation,
                "related_memories": json.loads(mem.related_memories) if mem.related_memories else [],
                "access_count": mem.access_count,
                "created_at": mem.created_at.isoformat() if mem.created_at else None,
                "embedding": json.loads(mem.embedding) if mem.embedding else None
            }
            training_data["memories"].append(memory_data)
        
        # Process agent logs
        for log in agent_logs:
            log_data = {
                "agent_type": log.agent_type,
                "action": log.action,
                "input_data": json.loads(log.input_data) if log.input_data else None,
                "output_data": json.loads(log.output_data) if log.output_data else None,
                "execution_time": log.execution_time,
                "confidence_score": log.confidence_score,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "success": log.success
            }
            training_data["agent_logs"].append(log_data)
        
        return training_data
    
    async def export_all_training_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Export all conversations marked for training"""
        query = select(Conversation).where(
            Conversation.training_data_exported == False
        ).order_by(Conversation.started_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        conversations = result.scalars().all()
        
        training_data = []
        for conv in conversations:
            data = await self.export_conversation(conv.id)
            if data:
                training_data.append(data)
        
        return training_data
    
    async def mark_exported(self, conversation_id: int):
        """Mark conversation as exported"""
        from sqlalchemy import update
        await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(training_data_exported=True)
        )
        await self.session.commit()
