"""
Enhanced chat routes with all advanced features
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from core.session_manager import AIFriendSessions
# from api.routes.auth import get_current_user
from .user import get_anonymous_user as get_current_user

from memory.semantic_memory import SemanticMemoryEngine
from agents.advanced_emotion_analyzer import AdvancedEmotionAnalyzer
from utils.logger import Logger
from sse_starlette.sse import EventSourceResponse
import asyncio

router = APIRouter()
logger = Logger("ChatRoute")

# Global instances
sessions = AIFriendSessions()
semantic_memory = SemanticMemoryEngine()
emotion_analyzer = AdvancedEmotionAnalyzer()

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: bool = True

class ChatResponse(BaseModel):
    response: str
    emotion: Dict[str, Any]
    processing_time: float
    memories_used: int
    session_id: str

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    '''Send message with full AI processing - Optimized for speed'''
    try:
        # Get user session
        session = await sessions.get_or_create(user_id)
        
        # Run emotion analysis and memory search in parallel for speed
        emotion_task = emotion_analyzer.analyze(request.message)
        memory_task = semantic_memory.search_memories(user_id, request.message, n_results=3)
        chat_task = session.chat(request.message)
        
        # Wait for all in parallel
        emotion_analysis, relevant_memories, result = await asyncio.gather(
            emotion_task, memory_task, chat_task
        )
        
        # Save to semantic memory in background (non-blocking)
        if request.save_to_memory and emotion_analysis.get('confidence', 0) > 0.6:
            asyncio.create_task(
                semantic_memory.save_memory(
                    user_id,
                    request.message,
                    {
                        'emotion': emotion_analysis.get('primary_emotion', 'neutral'),
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'importance': emotion_analysis.get('confidence', 0.5)
                    }
                )
            )
        
        return ChatResponse(
            response=result['response'],
            emotion=emotion_analysis,
            processing_time=result['processing_time'],
            memories_used=len(relevant_memories),
            session_id=session.ai_friend.session_id
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream")
async def stream_chat(
    message: str,
    user_id: str = Depends(get_current_user)
):
    '''Streaming chat response (like ChatGPT)'''
    
    async def generate():
        session = await sessions.get_or_create(user_id)
        result = await session.chat(message)
        
        # Simulate streaming by splitting response
        words = result['response'].split()
        for word in words:
            yield {
                "event": "message",
                "data": word + " "
            }
            await asyncio.sleep(0.05)  # Simulate typing
        
        yield {
            "event": "done",
            "data": "complete"
        }
    
    return EventSourceResponse(generate())

@router.websocket("/ws/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    '''WebSocket for real-time bidirectional chat'''
    await websocket.accept()
    
    try:
        session = await sessions.get_or_create(user_id)
        
        while True:
            data = await websocket.receive_text()
            result = await session.chat(data)
            
            await websocket.send_json({
                'response': result['response'],
                'emotion': result['emotion'],
                'processing_time': result['processing_time']
            })
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

@router.get("/history")
async def get_chat_history(
    user_id: str = Depends(get_current_user),
    limit: int = 50
):
    '''Get conversation history'''
    session = await sessions.get_or_create(user_id)
    summary = await session.ai_friend.get_conversation_summary()
    return summary

@router.delete("/clear")
async def clear_conversation(user_id: str = Depends(get_current_user)):
    '''Clear conversation and start fresh'''
    await sessions.remove(user_id)
    # Clear cache for this user
    from core.response_cache import response_cache
    await response_cache.clear_user_cache(user_id)
    return {"message": "Conversation cleared"}

@router.get("/performance")
async def get_performance_stats():
    '''Get performance statistics'''
    from core.performance_monitor import perf_monitor
    from core.response_cache import response_cache
    
    return {
        "performance": perf_monitor.get_stats(),
        "cache": response_cache.get_stats()
    }