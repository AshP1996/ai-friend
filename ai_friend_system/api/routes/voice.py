"""
Advanced voice routes with streaming and wake-word detection
"""
import asyncio
from api.routes.auth import verify_token
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Depends, Query
# from api.routes.auth import get_current_user
from .user import get_anonymous_user as get_current_user

from voice.audio_manager import AudioManager
import logging

router = APIRouter()
logger = logging.getLogger("VOICE")


# ==============================
# VOICE ENGINE
# ==============================
class VoiceEngine:
    def __init__(self):
        self.audio_managers: dict[str, AudioManager] = {}

    def get_manager(self, user_id: str) -> AudioManager:
        if user_id not in self.audio_managers:
            manager = AudioManager()
            manager.initialize()
            self.audio_managers[user_id] = manager
        return self.audio_managers[user_id]

    def cleanup(self, user_id: str):
        if user_id in self.audio_managers:
            try:
                self.audio_managers[user_id].shutdown()
            except Exception:
                pass
            del self.audio_managers[user_id]


voice_engine = VoiceEngine()


# ==============================
# REST: SPEECH → TEXT
# ==============================
@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    audio_data = await audio.read()

    # TODO: run STT engine here
    text = "Recognized text"

    return {
        "text": text,
        "confidence": 0.95
    }


# ==============================
# REST: TEXT → SPEECH
# ==============================
@router.post("/tts")
async def text_to_speech(
    text: str,
    emotion: str = "neutral",
    user_id: str = Depends(get_current_user)
):
    manager = voice_engine.get_manager(user_id)
    await manager.speak(text, emotion)
    return {"status": "speaking"}


# ==============================
# WEBSOCKET: REAL-TIME VOICE
# ==============================
@router.websocket("/stream/{user_id}")
async def voice_stream(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):
    if user_id in ("undefined", "null", ""):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    logger.info(f"🎤 Voice connected | user={user_id}")

    manager = voice_engine.get_manager(user_id)
    last_audio_time = asyncio.get_event_loop().time()

    try:
        while True:
            try:
                audio_chunk = await asyncio.wait_for(
                    websocket.receive_bytes(),
                    timeout=8.0
                )
            except asyncio.TimeoutError:
                logger.info("⏳ No audio received, closing stream")
                break

            if not audio_chunk:
                continue

            last_audio_time = asyncio.get_event_loop().time()

            # text = manager.stt.process_pcm(audio_chunk)
            text = manager.process_pcm(audio_chunk)


            if text:
                await websocket.send_json({
                    "type": "result",
                    "text": text
                })

    except WebSocketDisconnect:
        logger.info(f"🔌 Disconnected | user={user_id}")

    finally:
        voice_engine.cleanup(user_id)
        await websocket.close()

# ==============================
# AUDIO DEVICES
# ==============================
@router.get("/devices")
async def get_audio_devices(
    user_id: str = Depends(get_current_user)
):
    manager = voice_engine.get_manager(user_id)
    devices = manager.get_available_devices()

    return {"devices": devices}
