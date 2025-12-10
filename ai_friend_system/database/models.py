from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from config.constants import MemoryTier, MessageType, EmotionType

@dataclass
class ConversationModel:
    id: Optional[int]
    session_id: str
    user_id: str
    started_at: datetime
    last_active: datetime
    is_active: bool = True

@dataclass
class MessageModel:
    id: Optional[int]
    conversation_id: int
    role: str
    content: str
    emotion: Optional[str]
    timestamp: datetime
    processing_time: Optional[float]
    memory_tier: Optional[str]
    importance_score: float = 0.5

@dataclass
class MemoryModel:
    id: Optional[int]
    conversation_id: int
    tier: str
    content: str
    context: Optional[str]
    tags: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    importance: float = 0.5
    last_accessed: datetime = None