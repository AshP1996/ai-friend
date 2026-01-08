from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from config.constants import MemoryTier, MessageType, EmotionType

@dataclass(slots=True)
class ConversationModel:
    id: Optional[int]
    session_id: str
    user_id: str

    model_used: str = "default"
    language: str = "en"
    platform: str = "unknown"

    started_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


# @dataclass
# class MessageModel:
#     id: Optional[int]
#     conversation_id: int
#     role: str
#     content: str
#     emotion: Optional[str]
#     timestamp: datetime
#     processing_time: Optional[float]
#     memory_tier: Optional[str]
#     importance_score: float = 0.5

from dataclasses import dataclass, field
from typing import Optional
from config.constants import MessageType, EmotionType

@dataclass(slots=True)
class MessageModel:
    id: Optional[int]
    conversation_id: int

    role: MessageType
    content: str

    emotion: EmotionType = EmotionType.NEUTRAL
    confidence: float = 0.5

    model_used: str = "default"
    tokens_used: Optional[int] = None

    processing_time: Optional[float] = None
    memory_tier: Optional[str] = None

    # Training data fields
    context_embedding: Optional[str] = None  # JSON
    agent_outputs: Optional[str] = None     # JSON
    memory_context: Optional[str] = None    # JSON
    user_feedback: Optional[float] = None   # 1-5 rating
    quality_score: Optional[float] = None
    training_flag: bool = False
    
    # Voice-specific fields
    voice_pitch: Optional[float] = None
    voice_emotion: Optional[str] = None
    audio_quality: Optional[float] = None

    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance_score: float = 0.5

@dataclass(slots=True)
class MemoryModel:
    id: Optional[int]
    conversation_id: int

    tier: MemoryTier
    content: str

    source: str = "user"  # user / ai / system
    context: Optional[str] = None
    tags: Optional[str] = None

    embedding: Optional[str] = None  # vector (JSON / base64)
    confidence: float = 1.0

    # Enhanced metadata
    emotion_at_creation: Optional[str] = None
    related_memories: Optional[str] = None  # JSON array
    training_relevance: Optional[float] = None
    verified: bool = False

    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    access_count: int = 0
    importance: float = 0.5
    last_accessed: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class PersonaModel:
    id: Optional[int]
    user_id: str
    
    name: str = "Friend"
    personality_traits: Dict[str, float] = field(default_factory=lambda: {
        "friendliness": 0.9,
        "humor": 0.7,
        "empathy": 0.9,
        "formality": 0.3
    })
    speaking_style: str = "casual"
    interests: List[str] = field(default_factory=lambda: ["technology", "music", "books"])
    background_story: Optional[str] = None
    voice_id: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
