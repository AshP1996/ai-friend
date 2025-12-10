from enum import Enum

class MemoryTier(Enum):
    SESSION = "session"
    SUB_TEMPORARY = "sub_temporary"
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    PERSONAL = "personal"

class MessageType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class EmotionType(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CONFUSED = "confused"
    EMPATHETIC = "empathetic"

class AgentType(Enum):
    TASK = "task"
    EMOTION = "emotion"
    CONTEXT = "context"