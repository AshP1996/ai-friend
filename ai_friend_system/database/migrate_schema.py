"""
Database migration script to add training data fields
Run this to update existing database with new columns

Usage:
    cd /home/ashish/Documents/fbot3/ai_friend_system
    source ../venv/bin/activate  # Activate virtual environment
    python database/migrate_schema.py
"""
import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
except ImportError as e:
    print("ERROR: Missing dependencies. Please activate virtual environment:")
    print("  source ../venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)

try:
    from config import settings
    from utils.logger import Logger
except ImportError as e:
    print(f"ERROR: Cannot import config or utils: {e}")
    print("Make sure you're running from the ai_friend_system directory")
    sys.exit(1)

logger = Logger("Migration")

async def migrate_database():
    """Add new columns for training data"""
    db_path = settings.database_path
    database_url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(database_url, echo=False)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check and add columns to messages table
            logger.info("Migrating messages table...")
            
            # Get existing columns
            result = await session.execute(text("PRAGMA table_info(messages)"))
            existing_columns = [row[1] for row in result]
            
            # Add new columns if they don't exist
            new_columns = {
                "context_embedding": "TEXT",
                "agent_outputs": "TEXT",
                "memory_context": "TEXT",
                "user_feedback": "REAL",
                "quality_score": "REAL",
                "training_flag": "INTEGER DEFAULT 0",
                "voice_pitch": "REAL",
                "voice_emotion": "TEXT",
                "audio_quality": "REAL"
            }
            
            for col_name, col_type in new_columns.items():
                if col_name not in existing_columns:
                    try:
                        await session.execute(
                            text(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
                        )
                        logger.info(f"✅ Added column: messages.{col_name}")
                    except Exception as e:
                        logger.warning(f"Column {col_name} may already exist: {e}")
            
            # Migrate conversations table
            logger.info("Migrating conversations table...")
            result = await session.execute(text("PRAGMA table_info(conversations)"))
            existing_columns = [row[1] for row in result]
            
            conv_columns = {
                "total_messages": "INTEGER DEFAULT 0",
                "avg_response_time": "REAL",
                "avg_emotion_score": "REAL",
                "conversation_quality": "REAL",
                "user_satisfaction": "REAL",
                "topics_discussed": "TEXT",
                "training_data_exported": "INTEGER DEFAULT 0",
                "ended_at": "DATETIME"
            }
            
            for col_name, col_type in conv_columns.items():
                if col_name not in existing_columns:
                    try:
                        await session.execute(
                            text(f"ALTER TABLE conversations ADD COLUMN {col_name} {col_type}")
                        )
                        logger.info(f"✅ Added column: conversations.{col_name}")
                    except Exception as e:
                        logger.warning(f"Column {col_name} may already exist: {e}")
            
            # Migrate memories table
            logger.info("Migrating memories table...")
            result = await session.execute(text("PRAGMA table_info(memories)"))
            existing_columns = [row[1] for row in result]
            
            mem_columns = {
                "context": "TEXT",
                "tags": "TEXT",
                "emotion_at_creation": "TEXT",
                "related_memories": "TEXT",
                "access_count": "INTEGER DEFAULT 0",
                "training_relevance": "REAL",
                "verified": "INTEGER DEFAULT 0"
            }
            
            for col_name, col_type in mem_columns.items():
                if col_name not in existing_columns:
                    try:
                        await session.execute(
                            text(f"ALTER TABLE memories ADD COLUMN {col_name} {col_type}")
                        )
                        logger.info(f"✅ Added column: memories.{col_name}")
                    except Exception as e:
                        logger.warning(f"Column {col_name} may already exist: {e}")
            
            # Migrate agent_logs table
            logger.info("Migrating agent_logs table...")
            result = await session.execute(text("PRAGMA table_info(agent_logs)"))
            existing_columns = [row[1] for row in result]
            
            agent_columns = {
                "conversation_id": "INTEGER",
                "message_id": "INTEGER",
                "confidence_score": "REAL",
                "accuracy_score": "REAL",
                "training_quality": "REAL"
            }
            
            for col_name, col_type in agent_columns.items():
                if col_name not in existing_columns:
                    try:
                        await session.execute(
                            text(f"ALTER TABLE agent_logs ADD COLUMN {col_name} {col_type}")
                        )
                        logger.info(f"✅ Added column: agent_logs.{col_name}")
                    except Exception as e:
                        logger.warning(f"Column {col_name} may already exist: {e}")
            
            await session.commit()
            logger.info("✅ Migration complete!")
            
    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_database())
