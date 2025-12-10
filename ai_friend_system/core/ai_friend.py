# from typing import Optional, Dict, Any
# from datetime import datetime
# import uuid
# from sqlalchemy.ext.asyncio import AsyncSession
# from database import DatabaseManager
# from database.init_db import create_database, verify_database
# from memory import MemoryManager
# from voice import AudioManager
# from .message_processor import MessageProcessor
# from .response_generator import ResponseGenerator
# from utils.logger import Logger
# from config import settings, db_config

# class AIFriend:
#     def __init__(self):
#         self.logger = Logger("AIFriend")
#         self.db_manager = DatabaseManager()
#         self.memory_manager = MemoryManager(self.db_manager)
#         self.audio_manager = AudioManager()
#         self.message_processor = MessageProcessor(self.db_manager, self.memory_manager)
#         self.response_generator = ResponseGenerator()
        
#         self.conversation_id = None
#         self.session_id = str(uuid.uuid4())
#         self.user_id = "default_user"
#         self.is_initialized = False
    
#     async def initialize(self):
#         if self.is_initialized:
#             return
        
#         try:
#             if not settings.database_path.exists():
#                 self.logger.info("Creating database...")
#                 await create_database()
#             else:
#                 if not await verify_database():
#                     await create_database()
            
#             db_config.initialize(settings.database_path)
#             await db_config.create_tables()
#             self.logger.info("Database initialized")
            
#             audio_ok = self.audio_manager.initialize()
#             if not audio_ok:
#                 self.logger.warning("Audio not available")
            
#             self.is_initialized = True
#             self.logger.info("AI Friend initialized")
#         except Exception as e:
#             self.logger.error(f"Init error: {e}")
#             raise
    
#     async def start_conversation(self, user_id: str = None):
#         if user_id:
#             self.user_id = user_id
        
#         async for session in db_config.get_session():
#             self.conversation_id = await self.db_manager.create_conversation(
#                 session, self.user_id, self.session_id
#             )
#             await session.commit()
        
#         self.logger.info(f"Started conversation {self.conversation_id}")
#         return self.conversation_id
    
#     async def chat(self, user_message: str) -> Dict[str, Any]:
#         """Main chat - ALWAYS returns valid response"""
#         if not self.conversation_id:
#             await self.start_conversation()
        
#         start_time = datetime.now()
        
#         # Safe defaults
#         safe_response = {
#             'response': "I'm here! Let's chat!",
#             'emotion': {'emotion': 'neutral', 'confidence': 0.5},
#             'processing_time': 0.0,
#             'memories_used': 0
#         }
        
#         try:
#             async for session in db_config.get_session():
#                 # Process message
#                 processed = await self.message_processor.process_message(
#                     session, self.conversation_id, user_message
#                 )
                
#                 # Build context
#                 agent_results = processed.get('agent_results', {})
#                 context = {
#                     'emotion': agent_results.get('emotion', {}),
#                     'user_name': self.user_id,
#                     'memories': processed.get('memories', [])
#                 }
                
#                 messages = processed.get('history', []) + [
#                     {'role': 'user', 'content': user_message}
#                 ]
                
#                 # Generate response - GUARANTEED to return string
#                 response_text = await self.response_generator.generate_response(messages, context)
                
#                 # Validate
#                 if not response_text or not isinstance(response_text, str):
#                     response_text = "I'm listening! Tell me more."
                
#                 # Save response
#                 from database.models import MessageModel
#                 from config.constants import MessageType
                
#                 emotion_data = agent_results.get('emotion', {})
#                 emotion = emotion_data.get('emotion', 'neutral') if isinstance(emotion_data, dict) else 'neutral'
                
#                 response_msg = MessageModel(
#                     id=None,
#                     conversation_id=self.conversation_id,
#                     role=MessageType.ASSISTANT.value,
#                     content=response_text,
#                     emotion=emotion,
#                     timestamp=datetime.now(),
#                     processing_time=(datetime.now() - start_time).total_seconds(),
#                     memory_tier=None,
#                     importance_score=0.7
#                 )
                
#                 await self.db_manager.save_message(session, response_msg)
#                 await session.commit()
            
#             return {
#                 'response': response_text,
#                 'emotion': agent_results.get('emotion', {'emotion': 'neutral'}),
#                 'processing_time': (datetime.now() - start_time).total_seconds(),
#                 'memories_used': len(processed.get('memories', []))
#             }
            
#         except Exception as e:
#             self.logger.error(f"Chat error: {e}")
#             return safe_response
    
#     async def voice_chat(self, listen_timeout: int = 5) -> Optional[Dict[str, Any]]:
#         user_message = await self.audio_manager.listen(timeout=listen_timeout)
#         if not user_message:
#             return None
        
#         result = await self.chat(user_message)
#         await self.audio_manager.speak(result.get('response', 'I heard you!'))
#         return result
    
#     async def get_conversation_summary(self) -> Dict[str, Any]:
#         if not self.conversation_id:
#             return {
#                 'conversation_id': None,
#                 'stats': {'message_count': 0, 'avg_processing_time': 0}
#             }
        
#         try:
#             async for session in db_config.get_session():
#                 from database.queries import Queries
#                 stats = await Queries.get_conversation_stats(session, self.conversation_id)
#                 return {
#                     'conversation_id': self.conversation_id,
#                     'session_id': self.session_id,
#                     'user_id': self.user_id,
#                     'stats': stats
#                 }
#         except Exception as e:
#             self.logger.error(f"Summary error: {e}")
#             return {
#                 'conversation_id': self.conversation_id,
#                 'stats': {'message_count': 0, 'avg_processing_time': 0}
#             }


from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from database import DatabaseManager
from database.init_db import create_database, verify_database
from memory import MemoryManager
from voice import AudioManager
from .message_processor import *
from .response_generator import ResponseGenerator
from utils.logger import Logger
from config import settings, db_config


class AIFriend:
    def __init__(self):
        self.logger = Logger("AIFriend")

        # CORE MANAGERS
        self.db_manager = DatabaseManager()
        self.memory_manager = MemoryManager(self.db_manager)
        self.audio_manager = AudioManager()
        self.message_processor = MessageProcessor(self.db_manager, self.memory_manager)
        self.response_generator = ResponseGenerator()

        # SESSION DATA
        self.conversation_id = None
        self.session_id = str(uuid.uuid4())
        self.user_id = "default_user"
        self.is_initialized = False

    # INITIALIZE SYSTEM --------------------------------------------------------
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

            # AUDIO INIT
            audio_ok = self.audio_manager.initialize()
            if not audio_ok:
                self.logger.warning("Audio not available")

            self.is_initialized = True
            self.logger.info("AI Friend initialized")

        except Exception as e:
            self.logger.error(f"Init error: {e}")
            raise

    # START NEW CONVERSATION ---------------------------------------------------
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

    # MAIN CHAT FUNCTION -------------------------------------------------------
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Main chat function.
        ALWAYS returns a valid response (never crashes).
        """
        if not self.conversation_id:
            await self.start_conversation()

        start_time = datetime.now()

        # SAFETY DEFAULT RESPONSE
        safe_response = {
            "response": "I'm here! Let's chat!",
            "emotion": {"emotion": "neutral", "confidence": 0.5},
            "processing_time": 0.0,
            "memories_used": 0,
        }

        try:
            async for session in db_config.get_session():

                # ---- PROCESS USER MESSAGE ----
                processed = await self.message_processor.process_message(
                    session, self.conversation_id, user_message
                )

                agent_results = processed.get("agent_results", {})
                memories = processed.get("memories", [])
                history = processed.get("history", [])

                # Ensure history is list
                if not isinstance(history, list):
                    history = []

                # ---- BUILD CONTEXT ----
                context = {
                    "emotion": agent_results.get("emotion", {}),
                    "user_name": self.user_id,
                    "memories": memories,
                }

                # ---- FINAL MESSAGES FOR AI ----
                messages = history + [{"role": "user", "content": user_message}]

                # ---- GENERATE RESPONSE ----
                response_text = await self.response_generator.generate_response(
                    messages, context
                )

                # VALIDATE RESPONSE
                if not response_text or not isinstance(response_text, str):
                    response_text = "I'm listening! Tell me more."

                # ---- SAVE RESPONSE TO DB ----
                from database.models import MessageModel
                from config.constants import MessageType

                emotion_data = agent_results.get("emotion", {})
                emotion = (
                    emotion_data.get("emotion", "neutral")
                    if isinstance(emotion_data, dict)
                    else "neutral"
                )

                response_msg = MessageModel(
                    id=None,
                    conversation_id=self.conversation_id,
                    role=MessageType.ASSISTANT.value,
                    content=response_text,
                    emotion=emotion,
                    timestamp=datetime.now(),
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    memory_tier=None,
                    importance_score=0.7,
                )

                await self.db_manager.save_message(session, response_msg)
                await session.commit()

            # RETURN FINAL DATA
            return {
                "response": response_text,
                "emotion": agent_results.get(
                    "emotion", {"emotion": "neutral", "confidence": 0.5}
                ),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "memories_used": len(memories),
            }

        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return safe_response

    # VOICE CHAT ---------------------------------------------------------------
    async def voice_chat(self, listen_timeout: int = 5) -> Optional[Dict[str, Any]]:
        user_message = await self.audio_manager.listen(timeout=listen_timeout)
        if not user_message:
            return None

        result = await self.chat(user_message)
        await self.audio_manager.speak(result.get("response", "I heard you!"))
        return result

    # GET SUMMARY --------------------------------------------------------------
    async def get_conversation_summary(self) -> Dict[str, Any]:
        if not self.conversation_id:
            return {
                "conversation_id": None,
                "stats": {"message_count": 0, "avg_processing_time": 0},
            }

        try:
            async for session in db_config.get_session():
                from database.queries import Queries

                stats = await Queries.get_conversation_stats(
                    session, self.conversation_id
                )

                return {
                    "conversation_id": self.conversation_id,
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "stats": stats,
                }

        except Exception as e:
            self.logger.error(f"Summary error: {e}")
            return {
                "conversation_id": self.conversation_id,
                "stats": {"message_count": 0, "avg_processing_time": 0},
            }
