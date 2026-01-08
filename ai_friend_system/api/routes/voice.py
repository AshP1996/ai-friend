# import asyncio
# import logging
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
# from fastapi.responses import FileResponse

# from voice.audio_manager import AudioManager
# from .user import get_anonymous_user as get_current_user
# from core.session_manager import AIFriendSessions

# router = APIRouter()
# logger = logging.getLogger("VOICE")

# sessions = AIFriendSessions()


# # =====================================================
# # VOICE ENGINE (Per-user AudioManager)
# # =====================================================
# class VoiceEngine:
#     def __init__(self):
#         self._managers: dict[str, AudioManager] = {}
#         self._lock = asyncio.Lock()

#     async def get_manager(self, user_id: str) -> AudioManager:
#         async with self._lock:
#             manager = self._managers.get(user_id)

#             if manager is None:
#                 manager = AudioManager()
#                 manager.initialize()   # safe + useful
#                 self._managers[user_id] = manager

#             return manager

#     async def cleanup(self, user_id: str):
#         async with self._lock:
#             manager = self._managers.pop(user_id, None)

#         if manager:
#             try:
#                 manager.shutdown()
#             except Exception:
#                 logger.exception(
#                     f"Failed to shutdown AudioManager | {user_id}"
#                 )



# voice_engine = VoiceEngine()

# # =====================================================
# # REST: TEXT → SPEECH (OPTIONAL / DEBUG)
# # =====================================================
# @router.post("/tts")
# async def text_to_speech(
#     text: str,
#     emotion: str = "neutral",
#     user_id: str = Depends(get_current_user),
# ):
#     manager = await voice_engine.get_manager(user_id)
#     audio_bytes = await manager.text_to_speech(text, emotion)
#     return FileResponse(
#         content=audio_bytes,
#         media_type="audio/mpeg"
#     )


# # =====================================================
# # REST: FILE-BASED STT (OPTIONAL)
# # =====================================================
# @router.post("/stt")
# async def speech_to_text(
#     audio: UploadFile = File(...),
#     user_id: str = Depends(get_current_user),
# ):
#     manager = await voice_engine.get_manager(user_id)
#     audio_bytes = await audio.read()
#     result = manager.process_pcm(audio_bytes)
#     return {"text": result.get("final", "")}


# # =====================================================
# # WEBSOCKET: REAL-TIME VOICE (MAIN FEATURE)
# # =====================================================
# @router.websocket("/stream/{user_id}")
# async def voice_stream(websocket: WebSocket, user_id: str):
#     if not user_id or user_id in ("undefined", "null"):
#         await websocket.close(code=1008)
#         return

#     await websocket.accept()
#     logger.info(f"🎤 Voice connected | {user_id}")

#     manager = await voice_engine.get_manager(user_id)
#     session = await sessions.get_or_create(user_id)

#     loop = asyncio.get_running_loop()

#     try:
#         while True:
#             try:
#                 pcm_bytes = await asyncio.wait_for(
#                     websocket.receive_bytes(),
#                     timeout=30
#                 )
#             except asyncio.TimeoutError:
#                 await websocket.send_json({"type": "ping"})
#                 continue

#             # ===============================
#             # STT (run off event loop)
#             # ===============================
#             result = await loop.run_in_executor(
#                 None,
#                 manager.process_pcm,
#                 pcm_bytes
#             )

#             if result.get("partial"):
#                 await websocket.send_json({
#                     "type": "partial",
#                     "text": result["partial"]
#                 })

#             if result.get("final"):
#                 user_text = result["final"]

#                 # ===============================
#                 # AI CHAT
#                 # ===============================
#                 chat_result = await session.chat(user_text)
#                 ai_text = chat_result["response"]

#                 await websocket.send_json({
#                     "type": "final",
#                     "text": ai_text
#                 })

#                 # ===============================
#                 # TTS → BINARY FRAME
#                 # ===============================
#                 audio_bytes = await manager.text_to_speech(ai_text)
#                 await websocket.send_bytes(audio_bytes)

#     except WebSocketDisconnect:
#         logger.info(f"🔌 Voice disconnected | {user_id}")

#     except Exception as e:
#         logger.exception(f"Voice stream error | {user_id}: {e}")

#     finally:
#         await voice_engine.cleanup(user_id)
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from voice.audio_manager import AudioManager
from core.session_manager import AIFriendSessions

router = APIRouter()
logger = logging.getLogger("VOICE")

sessions = AIFriendSessions()


class VoiceEngine:
    def __init__(self):
        self._managers = {}
        self._lock = asyncio.Lock()

    async def get_manager(self, user_id: str) -> AudioManager:
        async with self._lock:
            if user_id not in self._managers:
                logger.info(f"🆕 Creating AudioManager | user={user_id}")
                manager = AudioManager()
                manager.initialize()
                self._managers[user_id] = manager
            return self._managers[user_id]

    async def cleanup(self, user_id: str):
        async with self._lock:
            manager = self._managers.pop(user_id, None)
        if manager:
            logger.info(f"🧹 Cleaning up AudioManager | user={user_id}")
            manager.shutdown()


voice_engine = VoiceEngine()


@router.websocket("/stream/{user_id}")
async def voice_stream(websocket: WebSocket, user_id: str):
    await websocket.accept()
    logger.info(f"🎤 Voice connected | user={user_id}")

    manager = await voice_engine.get_manager(user_id)
    session = await sessions.get_or_create(user_id)
    loop = asyncio.get_running_loop()

    try:
        await websocket.send_json({"type": "status", "state": "listening"})
        logger.info("👂 Listening for speech...")

        while True:
            pcm = await websocket.receive_bytes()
            logger.debug(f"🎧 PCM frame received ({len(pcm)} bytes)")

            result = await loop.run_in_executor(
                None,
                manager.process_pcm,
                pcm
            )

            if result.get("partial"):
                logger.debug(f"✏️ Partial sent: {result['partial']}")
                await websocket.send_json({
                    "type": "partial",
                    "text": result["partial"]
                })

            if result.get("final"):
                user_text = result["final"]
                logger.info(f"🧑 User said: {user_text}")

                manager.reset()

                await websocket.send_json({
                    "type": "status",
                    "state": "thinking",
                    "text": user_text
                })
                logger.info("🤔 AI thinking...")

                chat = await session.chat(user_text)
                ai_text = chat["response"]
                logger.info(f"🤖 AI response: {ai_text}")

                await websocket.send_json({
                    "type": "status",
                    "state": "speaking",
                    "text": ai_text
                })

                audio = await manager.text_to_speech(ai_text)
                logger.info("🔊 Sending TTS audio")
                await websocket.send_bytes(audio)

                await websocket.send_json({
                    "type": "status",
                    "state": "listening"
                })
                logger.info("👂 Listening again...")

    except WebSocketDisconnect:
        logger.info(f"🔌 Voice disconnected | user={user_id}")

    except Exception as e:
        logger.exception(f"❌ Voice error | user={user_id}: {e}")

    finally:
        await voice_engine.cleanup(user_id)
