from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from config.constants import MemoryTier, MessageType, EmotionType

# @dataclass
# class ConversationModel:
#     id: Optional[int]
#     session_id: str
#     user_id: str
#     started_at: datetime
#     last_active: datetime
#     is_active: bool = True

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

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

    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance_score: float = 0.5


# @dataclass
# class MemoryModel:
#     id: Optional[int]
#     conversation_id: int
#     tier: str
#     content: str
#     context: Optional[str]
#     tags: Optional[str]
#     created_at: datetime
#     expires_at: Optional[datetime]
#     access_count: int = 0
#     importance: float = 0.5
#     last_accessed: datetime = None

from dataclasses import dataclass, field
from typing import Optional
from config.constants import MemoryTier

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

    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    access_count: int = 0
    importance: float = 0.5
    last_accessed: datetime = field(default_factory=datetime.utcnow)
