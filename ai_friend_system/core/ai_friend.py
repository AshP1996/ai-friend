# from typing import Optional, Dict, Any
# from datetime import datetime
# import uuid
# from sqlalchemy.ext.asyncio import AsyncSession

# from database import DatabaseManager
# from database.init_db import create_database, verify_database
# from memory import MemoryManager
# from voice import AudioManager
# from .message_processor import *
# from .response_generator import ResponseGenerator
# from utils.logger import Logger
# from config import settings, db_config


# class AIFriend:
#     def __init__(self):
#         self.logger = Logger("AIFriend")

#         # CORE MANAGERS
#         self.db_manager = DatabaseManager()
#         self.memory_manager = MemoryManager(self.db_manager)
#         self.audio_manager = AudioManager()
#         self.message_processor = MessageProcessor(self.db_manager, self.memory_manager)
#         self.response_generator = ResponseGenerator()

#         # SESSION DATA
#         self.conversation_id = None
#         self.session_id = str(uuid.uuid4())
#         self.user_id = "default_user"
#         self.is_initialized = False

#     # INITIALIZE SYSTEM --------------------------------------------------------
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

#             # AUDIO INIT
#             audio_ok = self.audio_manager.initialize()
#             if not audio_ok:
#                 self.logger.warning("Audio not available")

#             self.is_initialized = True
#             self.logger.info("AI Friend initialized")

#         except Exception as e:
#             self.logger.error(f"Init error: {e}")
#             raise

#     # START NEW CONVERSATION ---------------------------------------------------
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

#     # MAIN CHAT FUNCTION -------------------------------------------------------
#     async def chat(self, user_message: str) -> Dict[str, Any]:
#         """
#         Main chat function.
#         ALWAYS returns a valid response (never crashes).
#         """
#         if not self.conversation_id:
#             await self.start_conversation()

#         start_time = datetime.now()

#         # SAFETY DEFAULT RESPONSE
#         safe_response = {
#             "response": "I'm here! Let's chat!",
#             "emotion": {"emotion": "neutral", "confidence": 0.5},
#             "processing_time": 0.0,
#             "memories_used": 0,
#         }

#         try:
#             async for session in db_config.get_session():

#                 # ---- PROCESS USER MESSAGE ----
#                 processed = await self.message_processor.process_message(
#                     session, self.conversation_id, user_message
#                 )

#                 agent_results = processed.get("agent_results", {})
#                 memories = processed.get("memories", [])
#                 history = processed.get("history", [])

#                 # Ensure history is list
#                 if not isinstance(history, list):
#                     history = []

#                 # ---- BUILD CONTEXT ----
#                 context = {
#                     "emotion": agent_results.get("emotion", {}),
#                     "user_name": self.user_id,
#                     "memories": memories,
#                 }

#                 # ---- FINAL MESSAGES FOR AI ----
#                 messages = history + [{"role": "user", "content": user_message}]

#                 # ---- GENERATE RESPONSE ----
#                 response_text = await self.response_generator.generate_response(
#                     messages, context
#                 )

#                 # VALIDATE RESPONSE
#                 if not response_text or not isinstance(response_text, str):
#                     response_text = "I'm listening! Tell me more."

#                 # ---- SAVE RESPONSE TO DB ----
#                 from database.models import MessageModel
#                 from config.constants import MessageType

#                 emotion_data = agent_results.get("emotion", {})
#                 emotion = (
#                     emotion_data.get("emotion", "neutral")
#                     if isinstance(emotion_data, dict)
#                     else "neutral"
#                 )

#                 response_msg = MessageModel(
#                     id=None,
#                     conversation_id=self.conversation_id,
#                     role=MessageType.ASSISTANT.value,
#                     content=response_text,
#                     emotion=emotion,
#                     timestamp=datetime.now(),
#                     processing_time=(datetime.now() - start_time).total_seconds(),
#                     memory_tier=None,
#                     importance_score=0.7,
#                 )

#                 await self.db_manager.save_message(session, response_msg)
#                 await session.commit()

#             # RETURN FINAL DATA
#             return {
#                 "response": response_text,
#                 "emotion": agent_results.get(
#                     "emotion", {"emotion": "neutral", "confidence": 0.5}
#                 ),
#                 "processing_time": (datetime.now() - start_time).total_seconds(),
#                 "memories_used": len(memories),
#             }

#         except Exception as e:
#             self.logger.error(f"Chat error: {e}")
#             return safe_response

#     # VOICE CHAT ---------------------------------------------------------------
#     async def voice_chat(self, listen_timeout: int = 5) -> Optional[Dict[str, Any]]:
#         user_message = await self.audio_manager.listen(timeout=listen_timeout)
#         if not user_message:
#             return None

#         result = await self.chat(user_message)
#         await self.audio_manager.speak(result.get("response", "I heard you!"))
#         return result

#     # GET SUMMARY --------------------------------------------------------------
#     async def get_conversation_summary(self) -> Dict[str, Any]:
#         if not self.conversation_id:
#             return {
#                 "conversation_id": None,
#                 "stats": {"message_count": 0, "avg_processing_time": 0},
#             }

#         try:
#             async for session in db_config.get_session():
#                 from database.queries import Queries

#                 stats = await Queries.get_conversation_stats(
#                     session, self.conversation_id
#                 )

#                 return {
#                     "conversation_id": self.conversation_id,
#                     "session_id": self.session_id,
#                     "user_id": self.user_id,
#                     "stats": stats,
#                 }

#         except Exception as e:
#             self.logger.error(f"Summary error: {e}")
#             return {
#                 "conversation_id": self.conversation_id,
#                 "stats": {"message_count": 0, "avg_processing_time": 0},
#             }

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio

from database import DatabaseManager
from database.init_db import create_database, verify_database
from memory import MemoryManager
from voice import AudioManager

from .message_processor import MessageProcessor
from .response_generator import ResponseGenerator

from utils.logger import Logger
from config import settings, db_config
from config.constants import MessageType, EmotionType


class AIFriend:
    """
    Central AI Orchestrator
    -----------------------
    Controls:
    - Conversation lifecycle
    - AI reasoning
    - Memory usage
    - Voice interaction
    """

    def __init__(self):
        self.logger = Logger("AIFriend")

        # IDs
        self.session_id = str(uuid.uuid4())
        self.user_id: str = "default_user"
        self.conversation_id: Optional[int] = None

        # Managers
        self.db_manager = DatabaseManager()
        self.memory_manager = MemoryManager(self.db_manager)
        self.audio_manager = AudioManager()

        self.message_processor = MessageProcessor(
            self.db_manager, self.memory_manager
        )
        self.response_generator = ResponseGenerator()

        # State
        self.initialized = False
        self.active = False

    # =====================================================
    # INITIALIZATION
    # =====================================================
    async def initialize(self):
        if self.initialized:
            return

        self.logger.info("Initializing AI Friend...")

        try:
            # ---- DATABASE ----
            if not settings.database_path.exists():
                await create_database()
            elif not await verify_database():
                await create_database()

            db_config.initialize(settings.database_path)
            await db_config.create_tables()

            # ---- AUDIO ----
            audio_ok = self.audio_manager.initialize()
            if not audio_ok:
                self.logger.warning("Voice system disabled")

            self.initialized = True
            self.logger.info("AI Friend ready")

        except Exception as e:
            self.logger.critical(f"Initialization failed: {e}")
            raise

    # =====================================================
    # CONVERSATION CONTROL
    # =====================================================
    async def start_conversation(self, user_id: Optional[str] = None):
        if user_id:
            self.user_id = user_id

        async for session in db_config.get_session():
            self.conversation_id = await self.db_manager.create_conversation(
                session, self.user_id, self.session_id
            )
            await session.commit()

        self.active = True
        self.logger.info(f"Conversation started ({self.conversation_id})")

    async def end_conversation(self):
        self.active = False
        self.logger.info("Conversation ended")

    # =====================================================
    # CORE CHAT PIPELINE
    # =====================================================
    async def chat(self, user_message: str) -> Dict[str, Any]:
        if not self.initialized:
            await self.initialize()

        if not self.conversation_id:
            await self.start_conversation()

        start_time = datetime.utcnow()

        try:
            async for session in db_config.get_session():

                # ---- PROCESS MESSAGE ----
                processed = await self.message_processor.process_message(
                    session=session,
                    conversation_id=self.conversation_id,
                    user_message=user_message
                ) or {}


                agent_results = processed.get("agent_results")
                if not isinstance(agent_results, dict):
                    agent_results = {}

                memories = processed.get("memories")
                if not isinstance(memories, list):
                    memories = []

                history = processed.get("history")
                if not isinstance(history, list):
                    history = []



                # ---- CONTEXT ----
                context = {
                    "emotion": agent_results.get("emotion"),
                    "memories": memories,
                    "user": self.user_id
                }

                # ---- RESPONSE GENERATION ----
                messages = history + [{"role": "user", "content": user_message}]
                response_text = await self.response_generator.generate_response(
                    messages, context
                )

                response_text = response_text or "I'm here with you."

                # ---- EMOTION ----
                emotion_data = agent_results.get("emotion", {})
                emotion = emotion_data.get(
                    "emotion", EmotionType.NEUTRAL
                )

                # ---- SAVE MESSAGE ----
                from database.models import MessageModel

                msg = MessageModel(
                    id=None,
                    conversation_id=self.conversation_id,
                    role=MessageType.ASSISTANT,
                    content=response_text,
                    emotion=emotion,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    memory_tier=None,
                    importance_score=0.7
                )

                await self.db_manager.save_message(session, msg)
                await session.commit()

            return {
                "response": response_text,
                "emotion": emotion_data,
                "processing_time": msg.processing_time,
                "memories_used": len(memories),
                "session_id": self.session_id
            }

        except Exception as e:
            self.logger.error(f"Chat pipeline failed: {e}")

            return {
                "response": "I'm having a small hiccup, but I'm still here.",
                "emotion": {"emotion": "neutral", "confidence": 0.4},
                "processing_time": 0.0,
                "memories_used": 0,
                "session_id": self.session_id
            }

    # =====================================================
    # VOICE CHAT (SYNC + CLI SAFE)
    # =====================================================
    async def voice_chat(
        self,
        listen_timeout: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Voice interaction handler

        Supports both:
        - listen_timeout (CLI / future API)
        - timeout (backward compatibility)

        :param listen_timeout: preferred listen timeout
        :param timeout: legacy timeout
        """

        if not self.audio_manager:
            self.logger.warning("Audio manager not available")
            return None

        # Resolve timeout safely
        final_timeout = listen_timeout if listen_timeout is not None else timeout

        try:
            self.logger.info("🎤 Listening for voice input...")

            # Audio input
            user_message = await self.audio_manager.listen(final_timeout)

            if not user_message:
                self.logger.info("No voice input detected")
                return None

            self.logger.info(f"🗣️ Heard: {user_message}")

            # Core chat
            result = await self.chat(user_message)

            # Speak response
            await self.audio_manager.speak(result["response"])

            return result

        except Exception as e:
            self.logger.error(f"Voice chat failed: {e}")
            return None


    # =====================================================
    # SUMMARY
    # =====================================================
    async def get_conversation_summary(self) -> Dict[str, Any]:
        if not self.conversation_id:
            return {"stats": {"message_count": 0}}

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
                    "stats": stats
                }

        except Exception as e:
            self.logger.error(f"Summary failed: {e}")
            return {"stats": {}}
