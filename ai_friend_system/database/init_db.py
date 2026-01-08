import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from config.database_config import Base
from config import settings
from utils.logger import Logger
from .schema import *
from datetime import datetime, timedelta

logger = Logger("DatabaseInit")

async def create_database():
    """Create database and all tables"""
    db_path = settings.database_path
    
    # Ensure data directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine
    database_url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(database_url, echo=False)
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info(f"Database created successfully at: {db_path}")
        
        # Create indexes for performance
        await create_indexes(engine)
        
        # Insert sample data (optional)
        await insert_sample_data(engine)
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        raise
    finally:
        await engine.dispose()

async def create_indexes(engine):
    """Create additional indexes for performance"""
    async with engine.begin() as conn:
        # Index for fast message retrieval
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_time 
            ON messages(conversation_id, timestamp DESC)
        """))
        
        # Index for memory search
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_memories_tier_importance 
            ON memories(tier, importance DESC, last_accessed DESC)
        """))
        
        # Index for memory expiration cleanup
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_memories_expires 
            ON memories(expires_at)
        """))
        
        logger.info("Database indexes created")

async def insert_sample_data(engine):
    """Insert sample data for testing"""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Create sample user profile
            from .schema import UserProfile
            
            sample_user = UserProfile(
                user_id="default_user",
                name="Friend",
                preferences='{"tone": "friendly", "formality": "casual"}',
                personality_traits='{"curious": true, "empathetic": true}',
                interests='["AI", "technology", "conversation"]',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            session.add(sample_user)
            await session.commit()
            
            logger.info("Sample data inserted")
            
        except Exception as e:
            logger.warning(f"Sample data insertion skipped: {e}")
            await session.rollback()

async def verify_database():
    """Verify database structure"""
    db_path = settings.database_path
    
    if not db_path.exists():
        logger.error("Database file does not exist!")
        return False
    
    database_url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check if all tables exist
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """))
            
            tables = [row[0] for row in result]
            
            expected_tables = [
                'conversations',
                'messages',
                'memories',
                'user_profiles',
                'personal_info',
                'agent_logs',
                'personas'
            ]
            
            # Verify new columns exist (for migration)
            logger.info("Verifying enhanced schema columns...")
            
            missing_tables = set(expected_tables) - set(tables)
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            logger.info(f"Database verification passed. Tables: {tables}")
            return True
            
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False
    finally:
        await engine.dispose()

async def drop_database():
    """Drop all tables (use with caution!)"""
    db_path = settings.database_path
    database_url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.warning("All database tables dropped!")
        
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise
    finally:
        await engine.dispose()

async def reset_database():
    """Reset database (drop and recreate)"""
    logger.warning("Resetting database...")
    await drop_database()
    await create_database()
    logger.info("Database reset complete!")

async def backup_database():
    """Create database backup"""
    db_path = settings.database_path
    backup_dir = db_path.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"ai_friend_backup_{timestamp}.db"
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    logger.info(f"Database backed up to: {backup_path}")
    
    # Keep only last 5 backups
    backups = sorted(backup_dir.glob("*.db"))
    if len(backups) > 5:
        for old_backup in backups[:-5]:
            old_backup.unlink()
            logger.info(f"Removed old backup: {old_backup}")

async def get_database_stats():
    """Get database statistics"""
    db_path = settings.database_path
    
    if not db_path.exists():
        return {"error": "Database does not exist"}
    
    database_url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(database_url, echo=False)
    
    stats = {}
    
    try:
        async with engine.begin() as conn:
            # Get table counts
            tables = ['conversations', 'messages', 'memories', 'user_profiles', 'personal_info', 'agent_logs']
            
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                stats[table] = count
            
            # Get database size
            stats['database_size_mb'] = db_path.stat().st_size / (1024 * 1024)
            
            # Get memory tier distribution
            result = await conn.execute(text("""
                SELECT tier, COUNT(*) as count 
                FROM memories 
                GROUP BY tier
            """))
            
            stats['memory_distribution'] = {row[0]: row[1] for row in result}
            
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        stats['error'] = str(e)
    finally:
        await engine.dispose()
    
    return stats

# CLI commands for database management
async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m database.init_db [command]")
        print("\nCommands:")
        print("  create   - Create database and tables")
        print("  verify   - Verify database structure")
        print("  reset    - Reset database (WARNING: deletes all data)")
        print("  backup   - Create database backup")
        print("  stats    - Show database statistics")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        await create_database()
    elif command == "verify":
        success = await verify_database()
        print(f"Verification: {'PASSED' if success else 'FAILED'}")
    elif command == "reset":
        confirm = input("Are you sure you want to reset the database? (yes/no): ")
        if confirm.lower() == 'yes':
            await reset_database()
        else:
            print("Reset cancelled")
    elif command == "backup":
        await backup_database()
    elif command == "stats":
        stats = await get_database_stats()
        print("\nDatabase Statistics:")
        print("=" * 50)
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())