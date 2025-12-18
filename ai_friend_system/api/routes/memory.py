"""
Advanced memory management routes
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from memory.semantic_memory import SemanticMemoryEngine
# from api.routes.auth import get_current_user
from .user import get_anonymous_user as get_current_user

router = APIRouter()
semantic_memory = SemanticMemoryEngine()

class MemorySaveRequest(BaseModel):
    content: str
    category: Optional[str] = "general"
    importance: float = 0.5
    tags: List[str] = []

class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 10
    category: Optional[str] = None

@router.post("/save")
async def save_memory(
    request: MemorySaveRequest,
    user_id: str = Depends(get_current_user)
):
    '''Save important memory'''
    metadata = {
        'category': request.category,
        'importance': request.importance,
        'tags': request.tags,
        'timestamp': str(datetime.now())
    }
    
    memory_id = await semantic_memory.save_memory(
        user_id,
        request.content,
        metadata
    )
    
    return {"memory_id": memory_id, "message": "Memory saved"}

@router.post("/search")
async def search_memories(
    request: MemorySearchRequest,
    user_id: str = Depends(get_current_user)
):
    '''Semantic search through memories'''
    memories = await semantic_memory.search_memories(
        user_id,
        request.query,
        n_results=request.limit
    )
    return {"memories": memories, "count": len(memories)}

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: str = Depends(get_current_user)
):
    '''Delete specific memory'''
    await semantic_memory.delete_memory(user_id, memory_id)
    return {"message": "Memory deleted"}

@router.get("/stats")
async def memory_stats(user_id: str = Depends(get_current_user)):
    '''Get memory statistics'''
    collection = semantic_memory.get_collection(user_id)
    count = collection.count()
    
    return {
        "total_memories": count,
        "user_id": user_id
    }