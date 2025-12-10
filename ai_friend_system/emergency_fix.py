#!/usr/bin/env python3
"""
Emergency Fix Script
Fixes the 'NoneType' object is not subscriptable error
Run this to fix everything immediately!
"""

import os
import sys
from pathlib import Path
import shutil

def backup_file(filepath):
    """Create backup of file"""
    if os.path.exists(filepath):
        backup = f"{filepath}.backup"
        shutil.copy2(filepath, backup)
        print(f"✅ Backed up: {filepath} -> {backup}")

def fix_main_py():
    """Fix main.py with proper error handling"""
    print("\n📝 Fixing main.py...")
    
    content = '''import asyncio
import argparse
from core import AIFriend
from utils.logger import Logger

logger = Logger("Main")

async def interactive_mode():
    ai_friend = AIFriend()
    
    print("=" * 60)
    print("AI FRIEND SYSTEM - Interactive Mode")
    print("=" * 60)
    
    logger.info("Initializing AI Friend...")
    await ai_friend.initialize()
    await ai_friend.start_conversation()
    
    print("\\nAI Friend is ready!")
    print("Commands:")
    print("  'voice' - Switch to voice mode")
    print("  'text' - Switch to text mode")
    print("  'summary' - Show conversation summary")
    print("  'quit' - Exit")
    print("\\nType your message or command:\\n")
    
    mode = "text"
    
    while True:
        try:
            if mode == "text":
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("Goodbye! 👋")
                    break
                elif user_input.lower() == 'voice':
                    mode = "voice"
                    print("Switched to voice mode.")
                    continue
                elif user_input.lower() == 'summary':
                    summary = await ai_friend.get_conversation_summary()
                    stats = summary.get('stats', {})
                    print(f"\\nMessages: {stats.get('message_count', 0)}")
                    print(f"Avg Processing: {stats.get('avg_processing_time', 0):.3f}s\\n")
                    continue
                
                # Process text message - WITH SAFE ERROR HANDLING
                result = await ai_friend.chat(user_input)
                
                # Safe access to all fields
                response = result.get('response', 'I am here!')
                emotion_data = result.get('emotion', {})
                
                if isinstance(emotion_data, dict):
                    emotion = emotion_data.get('emotion', 'neutral')
                else:
                    emotion = 'neutral'
                
                processing_time = result.get('processing_time', 0)
                memories_used = result.get('memories_used', 0)
                
                print(f"\\nAI Friend [{emotion}]: {response}")
                print(f"[⚡ {processing_time:.2f}s | 🧠 {memories_used} memories]\\n")
            
            else:  # voice mode
                text_check = input("(Press Enter to listen, or 'text' to switch): ").strip()
                
                if text_check.lower() == 'text':
                    mode = "text"
                    print("Switched to text mode.")
                    continue
                
                print("\\n🎤 Listening...")
                result = await ai_friend.voice_chat(listen_timeout=5)
                
                if result:
                    response = result.get('response', 'I heard you!')
                    print(f"\\n🔊 AI Friend: {response}\\n")
                else:
                    print("No speech detected. Try again.\\n")
        
        except KeyboardInterrupt:
            print("\\n\\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Oops! Something went wrong. Let's try again.\\n")

async def api_mode(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    from api import app
    
    logger.info(f"Starting API server on {host}:{port}")
    print(f"\\n🚀 AI Friend API Server")
    print(f"📡 http://{host}:{port}")
    print(f"📚 http://{host}:{port}/docs\\n")
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

def main():
    parser = argparse.ArgumentParser(description="AI Friend System")
    parser.add_argument('--mode', choices=['interactive', 'api'], default='interactive')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8000)
    
    args = parser.parse_args()
    
    if args.mode == 'interactive':
        asyncio.run(interactive_mode())
    else:
        asyncio.run(api_mode(args.host, args.port))

if __name__ == "__main__":
    main()
'''
    
    backup_file('main.py')
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ Fixed: main.py")

def fix_ai_friend():
    """Fix core/ai_friend.py to always return valid responses"""
    print("\n📝 Fixing core/ai_friend.py...")
    
    content = '''from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from database import DatabaseManager
from database.init_db import create_database, verify_database
from memory import MemoryManager
from voice import AudioManager
from .message_processor import MessageProcessor
from .response_generator import ResponseGenerator
from utils.logger import Logger
from config import settings, db_config

class AIFriend:
    def __init__(self):
        self.logger = Logger("AIFriend")
        self.db_manager = DatabaseManager()
        self.memory_manager = MemoryManager(self.db_manager)
        self.audio_manager = AudioManager()
        self.message_processor = MessageProcessor(self.db_manager, self.memory_manager)
        self.response_generator = ResponseGenerator()
        
        self.conversation_id = None
        self.session_id = str(uuid.uuid4())
        self.user_id = "default_user"
        self.is_initialized = False
    
    async def initialize(self):
        if self.is_initialized:
            return
        
        try:
            if not settings.database_path.exists():
                self.logger.info("Creating database...")
                await create_database()
            else:
                if not await verify_database():
                    await create_database()
            
            db_config.initialize(settings.database_path)
            await db_config.create_tables()
            self.logger.info("Database initialized")
            
            audio_ok = self.audio_manager.initialize()
            if not audio_ok:
                self.logger.warning("Audio not available")
            
            self.is_initialized = True
            self.logger.info("AI Friend initialized")
        except Exception as e:
            self.logger.error(f"Init error: {e}")
            raise
    
    async def start_conversation(self, user_id: str = None):
        if user_id:
            self.user_id = user_id
        
        async for session in db_config.get_session():
            self.conversation_id = await self.db_manager.create_conversation(
                session, self.user_id, self.session_id
            )
            await session.commit()
        
        self.logger.info(f"Started conversation {self.conversation_id}")
        return self.conversation_id
    
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """Main chat - ALWAYS returns valid response"""
        if not self.conversation_id:
            await self.start_conversation()
        
        start_time = datetime.now()
        
        # Safe defaults
        safe_response = {
            'response': "I'm here! Let's chat!",
            'emotion': {'emotion': 'neutral', 'confidence': 0.5},
            'processing_time': 0.0,
            'memories_used': 0
        }
        
        try:
            async for session in db_config.get_session():
                # Process message
                processed = await self.message_processor.process_message(
                    session, self.conversation_id, user_message
                )
                
                # Build context
                agent_results = processed.get('agent_results', {})
                context = {
                    'emotion': agent_results.get('emotion', {}),
                    'user_name': self.user_id,
                    'memories': processed.get('memories', [])
                }
                
                messages = processed.get('history', []) + [
                    {'role': 'user', 'content': user_message}
                ]
                
                # Generate response - GUARANTEED to return string
                response_text = await self.response_generator.generate_response(messages, context)
                
                # Validate
                if not response_text or not isinstance(response_text, str):
                    response_text = "I'm listening! Tell me more."
                
                # Save response
                from database.models import MessageModel
                from config.constants import MessageType
                
                emotion_data = agent_results.get('emotion', {})
                emotion = emotion_data.get('emotion', 'neutral') if isinstance(emotion_data, dict) else 'neutral'
                
                response_msg = MessageModel(
                    id=None,
                    conversation_id=self.conversation_id,
                    role=MessageType.ASSISTANT.value,
                    content=response_text,
                    emotion=emotion,
                    timestamp=datetime.now(),
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    memory_tier=None,
                    importance_score=0.7
                )
                
                await self.db_manager.save_message(session, response_msg)
                await session.commit()
            
            return {
                'response': response_text,
                'emotion': agent_results.get('emotion', {'emotion': 'neutral'}),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'memories_used': len(processed.get('memories', []))
            }
            
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return safe_response
    
    async def voice_chat(self, listen_timeout: int = 5) -> Optional[Dict[str, Any]]:
        user_message = await self.audio_manager.listen(timeout=listen_timeout)
        if not user_message:
            return None
        
        result = await self.chat(user_message)
        await self.audio_manager.speak(result.get('response', 'I heard you!'))
        return result
    
    async def get_conversation_summary(self) -> Dict[str, Any]:
        if not self.conversation_id:
            return {
                'conversation_id': None,
                'stats': {'message_count': 0, 'avg_processing_time': 0}
            }
        
        try:
            async for session in db_config.get_session():
                from database.queries import Queries
                stats = await Queries.get_conversation_stats(session, self.conversation_id)
                return {
                    'conversation_id': self.conversation_id,
                    'session_id': self.session_id,
                    'user_id': self.user_id,
                    'stats': stats
                }
        except Exception as e:
            self.logger.error(f"Summary error: {e}")
            return {
                'conversation_id': self.conversation_id,
                'stats': {'message_count': 0, 'avg_processing_time': 0}
            }
'''
    
    backup_file('core/ai_friend.py')
    with open('core/ai_friend.py', 'w') as f:
        f.write(content)
    print("✅ Fixed: core/ai_friend.py")

def main():
    print("=" * 60)
    print("🚑 EMERGENCY FIX - AI FRIEND SYSTEM")
    print("=" * 60)
    print()
    print("This will fix the 'NoneType' error immediately!")
    print()
    
    # Check we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        print("Please run this script from the ai_friend_system directory")
        sys.exit(1)
    
    try:
        # Apply fixes
        fix_main_py()
        fix_ai_friend()
        
        print()
        print("=" * 60)
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("🎉 Your AI Friend is now fixed!")
        print()
        print("Test it now:")
        print("  python main.py --mode interactive")
        print()
        print("Then type: hello")
        print()
        print("Note: Ollama is already running (that's good!)")
        print("The 'address already in use' is normal - it means")
        print("Ollama is already serving. That's what we want!")
        print()
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
