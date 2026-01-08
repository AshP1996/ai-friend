from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import asyncio
import time

from database import DatabaseManager
from database.init_db import create_database, verify_database
from memory import MemoryManager
from voice.audio_manager import AudioManager

from .message_processor import MessageProcessor
from .response_generator import ResponseGenerator
from .performance_monitor import perf_monitor, track_performance
from .conversation_flow import ConversationFlowTracker

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
        
        # Advanced: Conversation flow tracking
        self.flow_tracker = ConversationFlowTracker(max_history=10)

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
            # audio_ok = self.audio_manager.initialize()
            # if not audio_ok:
            #     self.logger.warning("Voice system disabled")

            self.logger.info("Voice system available (WebSocket mode)")

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
    @track_performance
    async def chat(self, user_message: str) -> Dict[str, Any]:
        if not self.initialized:
            await self.initialize()

        if not self.conversation_id:
            await self.start_conversation()

        start_time = time.perf_counter()

        try:
            # Optimized: Get session once and reuse
            async for session in db_config.get_session():

                # ---- PROCESS MESSAGE (optimized with parallel operations) ----
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



                # ---- ADVANCED: CONVERSATION FLOW TRACKING ----
                emotion_data = agent_results.get("emotion", {})
                detected_emotion = emotion_data.get("emotion", EmotionType.NEUTRAL) if isinstance(emotion_data, dict) else str(emotion_data) if emotion_data else EmotionType.NEUTRAL
                
                # Track conversation flow
                self.flow_tracker.track_message(user_message, detected_emotion)
                flow_context = self.flow_tracker.get_conversation_context()
                
                # ADVANCED: Re-retrieve memories with semantic scoring if needed
                # (memories from agent_results may not have semantic scoring)
                if not memories or len(memories) == 0:
                    conversation_context_for_memory = {
                        'emotion': agent_results.get("emotion"),
                        'current_topic': flow_context.get('current_topic'),
                        'emotion_trend': flow_context.get('emotion_trend')
                    }
                    memories = await self.memory_manager.retrieve_context(
                        session, self.conversation_id, user_message, conversation_context_for_memory
                    )
                
                # ---- CONTEXT (Enhanced with conversation flow) ----
                context = {
                    "emotion": agent_results.get("emotion"),
                    "memories": memories,
                    "user": self.user_id,
                    "user_name": self.user_id,  # Can be enhanced with actual name
                    "conversation_flow": flow_context  # Advanced: conversation context
                }

                # ---- RESPONSE GENERATION ----
                messages = history + [{"role": "user", "content": user_message}]
                
                # Debug: Log before generation
                self.logger.info(f"💬 Generating response for: '{user_message[:100]}...'")
                
                response_text = await self.response_generator.generate_response(
                    messages, context
                )

                response_text = response_text or "I'm here with you."
                
                # Debug: Log after generation
                self.logger.info(f"💬 Generated response: '{response_text[:100]}...'")
                self.logger.info(f"   Response length: {len(response_text)} chars")
                self.logger.info(f"   Word count: {len(response_text.split())} words")

                # ---- EMOTION ----
                emotion_data = agent_results.get("emotion", {})
                emotion = emotion_data.get(
                    "emotion", EmotionType.NEUTRAL
                )

                # ---- SAVE MESSAGE WITH TRAINING DATA ----
                from database.models import MessageModel
                import json

                processing_time = time.perf_counter() - start_time
                
                # Calculate quality score based on response characteristics
                quality_score = self._calculate_quality_score(
                    response_text, processing_time, emotion_data, memories
                )
                
                # Prepare training data
                agent_outputs_json = json.dumps(agent_results) if agent_results else None
                memory_context_json = json.dumps([
                    {"content": m.get("content", ""), "tier": m.get("tier", "")}
                    for m in memories[:5]
                ]) if memories else None
                
                msg = MessageModel(
                    id=None,
                    conversation_id=self.conversation_id,
                    role=MessageType.ASSISTANT,
                    content=response_text,
                    emotion=emotion,
                    confidence=emotion_data.get("confidence", 0.5) if isinstance(emotion_data, dict) else 0.5,
                    model_used=self.response_generator.ollama.model if self.response_generator.ollama.available else "default",
                    processing_time=processing_time,
                    memory_tier=None,
                    importance_score=0.7,
                    # Training data
                    agent_outputs=agent_outputs_json,
                    memory_context=memory_context_json,
                    quality_score=quality_score,
                    training_flag=True  # Mark for training by default
                )

                await self.db_manager.save_message(session, msg)
                await session.commit()

            # Track performance
            perf_monitor.track_response_time(processing_time)

            return {
                "response": response_text,
                "emotion": emotion_data,
                "processing_time": round(processing_time, 3),
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
    # async def voice_chat(
    #     self,
    #     listen_timeout: Optional[int] = None,
    #     timeout: Optional[int] = None
    # ) -> Optional[Dict[str, Any]]:
    #     """
    #     Voice interaction handler

    #     Supports both:
    #     - listen_timeout (CLI / future API)
    #     - timeout (backward compatibility)

    #     :param listen_timeout: preferred listen timeout
    #     :param timeout: legacy timeout
    #     """

    #     if not self.audio_manager:
    #         self.logger.warning("Audio manager not available")
    #         return None

    #     # Resolve timeout safely
    #     final_timeout = listen_timeout if listen_timeout is not None else timeout

    #     try:
    #         self.logger.info("🎤 Listening for voice input...")

    #         # Audio input
    #         user_message = await self.audio_manager.listen(final_timeout)

    #         if not user_message:
    #             self.logger.info("No voice input detected")
    #             return None

    #         self.logger.info(f"🗣️ Heard: {user_message}")

    #         # Core chat
    #         result = await self.chat(user_message)

    #         # Speak response
    #         await self.audio_manager.speak(result["response"])

    #         return result

    #     except Exception as e:
    #         self.logger.error(f"Voice chat failed: {e}")
    #         return None


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
    
    def _calculate_quality_score(self, response: str, processing_time: float, 
                                  emotion_data: Dict, memories: List) -> float:
        """Calculate quality score for training data"""
        score = 0.5  # Base score
        
        # Response length (optimal 20-100 words)
        word_count = len(response.split())
        if 20 <= word_count <= 100:
            score += 0.1
        elif word_count < 10:
            score -= 0.1
        
        # Processing time (faster is better, but not too fast)
        if 0.5 <= processing_time <= 3.0:
            score += 0.1
        elif processing_time > 5.0:
            score -= 0.1
        
        # Emotion confidence
        if isinstance(emotion_data, dict):
            conf = emotion_data.get("confidence", 0.5)
            score += (conf - 0.5) * 0.2
        
        # Memory usage (some context is good)
        if 1 <= len(memories) <= 5:
            score += 0.1
        
        return max(0.0, min(1.0, score))  # Clamp to 0-1