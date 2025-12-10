"""
Database Setup Script
Run this script first to initialize the database
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import create_database, verify_database, get_database_stats
from utils.logger import Logger

logger = Logger("Setup")

async def setup():
    print("=" * 60)
    print("AI FRIEND SYSTEM - Database Setup")
    print("=" * 60)
    print()
    
    logger.info("Starting database setup...")
    
    try:
        # Create database
        print("📦 Creating database and tables...")
        await create_database()
        print("✅ Database created successfully!")
        print()
        
        # Verify
        print("🔍 Verifying database structure...")
        if await verify_database():
            print("✅ Database verification passed!")
        else:
            print("❌ Database verification failed!")
            return
        print()
        
        # Show stats
        print("📊 Database Statistics:")
        stats = await get_database_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print()
        
        print("=" * 60)
        print("🎉 Database setup complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python main.py --mode interactive")
        print()
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup())
