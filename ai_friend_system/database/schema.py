from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from config.database_config import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)

    model_used = Column(String(100))        # GPT / LLaMA / Custom
    language = Column(String(20), default="en")
    platform = Column(String(50), index=True)  # web / mobile / voice

    # Training and analytics fields
    total_messages = Column(Integer, default=0)
    avg_response_time = Column(Float)
    avg_emotion_score = Column(Float)
    conversation_quality = Column(Float)    # Overall quality score
    user_satisfaction = Column(Float)       # User feedback average
    topics_discussed = Column(Text)         # JSON array of topics
    training_data_exported = Column(Boolean, default=False)
    
    started_at = Column(DateTime, default=func.now(), index=True)
    last_active = Column(DateTime, default=func.now(), onupdate=func.now())
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)

    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)

    emotion = Column(String(50), index=True)
    confidence = Column(Float)                # AI confidence
    model = Column(String(50))                # gpt-4, llama, etc

    tokens_used = Column(Integer)
    processing_time = Column(Float)

    # Training data fields
    context_embedding = Column(Text)         # Full context embedding (JSON)
    agent_outputs = Column(Text)             # All agent outputs (JSON)
    memory_context = Column(Text)            # Memories used (JSON)
    user_feedback = Column(Float)            # User rating (1-5)
    quality_score = Column(Float)            # Auto-calculated quality
    training_flag = Column(Boolean, default=False)  # Mark for training
    
    # Voice-specific fields
    voice_pitch = Column(Float)              # Detected pitch (Hz)
    voice_emotion = Column(String(50))       # Emotion from voice
    audio_quality = Column(Float)            # Audio quality score
    
    timestamp = Column(DateTime, default=func.now(), index=True)

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)

    tier = Column(String(50), index=True)  # session / temporary / permanent
    content = Column(Text, nullable=False)

    embedding = Column(Text)              # vector (JSON/string)
    source = Column(String(50), index=True)  # user / ai / system

    importance = Column(Float, default=0.5, index=True)
    confidence = Column(Float, default=1.0)

    # Enhanced metadata for training
    context = Column(Text)                # Full context when created
    tags = Column(Text)                   # Comma-separated tags
    emotion_at_creation = Column(String(50))  # Emotion when created
    related_memories = Column(Text)       # JSON array of related memory IDs
    access_count = Column(Integer, default=0, index=True)
    last_accessed = Column(DateTime, default=func.now(), index=True)
    
    # Training fields
    training_relevance = Column(Float)    # Relevance for training
    verified = Column(Boolean, default=False)  # Human verified
    
    created_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime, index=True)


class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200))
    preferences = Column(Text)
    personality_traits = Column(Text)
    interests = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PersonalInfo(Base):
    __tablename__ = 'personal_info'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), ForeignKey('user_profiles.user_id'), index=True)
    category = Column(String(100), index=True)
    key = Column(String(200))
    value = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AgentLog(Base):
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), index=True)
    
    agent_type = Column(String(50), index=True)
    action = Column(String(200))
    input_data = Column(Text)             # Full input context
    output_data = Column(Text)             # Full output (JSON)
    execution_time = Column(Float)
    
    # Training data
    confidence_score = Column(Float)      # Agent confidence
    accuracy_score = Column(Float)         # If verified
    training_quality = Column(Float)      # Quality for training
    
    timestamp = Column(DateTime, default=func.now(), index=True)
    success = Column(Boolean, default=True, index=True)

class Persona(Base):
    __tablename__ = 'personas'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    
    name = Column(String(200), default="Friend")
    personality_traits = Column(Text)  # JSON string
    speaking_style = Column(String(50), default="casual")
    interests = Column(Text)  # JSON string
    background_story = Column(Text)
    voice_id = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())