"""
Training data export and management APIs
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from database.training_data import TrainingDataExporter
from config import db_config
from .user import get_anonymous_user as get_current_user
from utils.logger import Logger

router = APIRouter()
logger = Logger("TrainingRoute")

class ExportRequest(BaseModel):
    conversation_id: Optional[int] = None
    limit: Optional[int] = None
    format: str = "json"  # json, csv, parquet

@router.post("/export")
async def export_training_data(
    request: ExportRequest,
    user_id: str = Depends(get_current_user)
):
    """Export training data for AI model training"""
    try:
        async for session in db_config.get_session():
            exporter = TrainingDataExporter(session)
            
            if request.conversation_id:
                # Export single conversation
                data = await exporter.export_conversation(request.conversation_id)
                if not data:
                    raise HTTPException(status_code=404, detail="Conversation not found")
                return {"data": data, "count": 1}
            else:
                # Export all conversations
                data = await exporter.export_all_training_data(limit=request.limit)
                return {"data": data, "count": len(data)}
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}")
async def get_training_conversation(
    conversation_id: int,
    user_id: str = Depends(get_current_user)
):
    """Get training data for a specific conversation"""
    try:
        async for session in db_config.get_session():
            exporter = TrainingDataExporter(session)
            data = await exporter.export_conversation(conversation_id)
            
            if not data:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-exported/{conversation_id}")
async def mark_conversation_exported(
    conversation_id: int,
    user_id: str = Depends(get_current_user)
):
    """Mark conversation as exported"""
    try:
        async for session in db_config.get_session():
            exporter = TrainingDataExporter(session)
            await exporter.mark_exported(conversation_id)
            return {"message": "Conversation marked as exported"}
    except Exception as e:
        logger.error(f"Mark exported error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_training_stats(user_id: str = Depends(get_current_user)):
    """Get training data statistics"""
    try:
        async for session in db_config.get_session():
            from sqlalchemy import select, func
            from database.schema import Conversation, Message
            
            # Total conversations
            conv_count = await session.execute(
                select(func.count(Conversation.id))
            )
            total_conversations = conv_count.scalar() or 0
            
            # Exported conversations
            exported_count = await session.execute(
                select(func.count(Conversation.id))
                .where(Conversation.training_data_exported == True)
            )
            exported_conversations = exported_count.scalar() or 0
            
            # Total messages
            msg_count = await session.execute(
                select(func.count(Message.id))
            )
            total_messages = msg_count.scalar() or 0
            
            # Messages marked for training
            training_msg_count = await session.execute(
                select(func.count(Message.id))
                .where(Message.training_flag == True)
            )
            training_messages = training_msg_count.scalar() or 0
            
            return {
                "total_conversations": total_conversations,
                "exported_conversations": exported_conversations,
                "pending_export": total_conversations - exported_conversations,
                "total_messages": total_messages,
                "training_messages": training_messages,
                "export_percentage": round((exported_conversations / total_conversations * 100) if total_conversations > 0 else 0, 2)
            }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
