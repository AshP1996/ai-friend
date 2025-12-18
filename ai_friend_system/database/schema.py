from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from config.database_config import Base

# class Conversation(Base):
#     __tablename__ = 'conversations'
    
#     id = Column(Integer, primary_key=True)
#     session_id = Column(String(100), unique=True, nullable=False, index=True)
#     user_id = Column(String(100), index=True)
#     started_at = Column(DateTime, default=func.now())
#     last_active = Column(DateTime, default=func.now(), onupdate=func.now())
#     is_active = Column(Boolean, default=True)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)

    model_used = Column(String(100))        # GPT / LLaMA / Custom
    language = Column(String(20), default="en")
    platform = Column(String(50))            # web / mobile / voice

    started_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)


# class Message(Base):
#     __tablename__ = 'messages'
    
#     id = Column(Integer, primary_key=True)
#     conversation_id = Column(Integer, ForeignKey('conversations.id'), index=True)
#     role = Column(String(20), nullable=False)
#     content = Column(Text, nullable=False)
#     emotion = Column(String(50))
#     timestamp = Column(DateTime, default=func.now(), index=True)
#     processing_time = Column(Float)
#     memory_tier = Column(String(50), index=True)
#     importance_score = Column(Float, default=0.5)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)

    emotion = Column(String(50))
    confidence = Column(Float)                # AI confidence
    model = Column(String(50))                # gpt-4, llama, etc

    tokens_used = Column(Integer)
    processing_time = Column(Float)

    timestamp = Column(DateTime, default=func.now(), index=True)


# class Memory(Base):
#     __tablename__ = 'memories'
    
#     id = Column(Integer, primary_key=True)
#     conversation_id = Column(Integer, ForeignKey('conversations.id'), index=True)
#     tier = Column(String(50), nullable=False, index=True)
#     content = Column(Text, nullable=False)
#     context = Column(Text)
#     tags = Column(String(500))
#     created_at = Column(DateTime, default=func.now(), index=True)
#     expires_at = Column(DateTime, index=True)
#     access_count = Column(Integer, default=0)
#     importance = Column(Float, default=0.5)
#     last_accessed = Column(DateTime, default=func.now())

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    tier = Column(String(50), index=True)  # short / long / core
    content = Column(Text, nullable=False)

    embedding = Column(Text)              # vector (JSON/string)
    source = Column(String(50))            # user / ai / system

    importance = Column(Float, default=0.5)
    confidence = Column(Float, default=1.0)

    created_at = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)


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
    agent_type = Column(String(50), index=True)
    action = Column(String(200))
    input_data = Column(Text)
    output_data = Column(Text)
    execution_time = Column(Float)
    timestamp = Column(DateTime, default=func.now(), index=True)
    success = Column(Boolean, default=True)