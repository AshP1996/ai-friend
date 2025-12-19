# voice/voice.py
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
from fastapi.responses import FileResponse
from voice.audio_manager import AudioManager
# from api.routes.auth import get_current_user
from .user import get_anonymous_user as get_current_user
import logging

router = APIRouter()
logger = logging.getLogger("VOICE")

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

# ===== REST: TTS =====
@router.post("/tts")
async def text_to_speech(text: str, emotion: str = "neutral", user_id: str = Depends(get_current_user)):
    manager = voice_engine.get_manager(user_id)
    audio_path = await manager.tts.generate_to_file(text, emotion)
    return FileResponse(audio_path, media_type="audio/wav", filename="response.wav")

# ===== REST: STT =====
@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    audio_data = await audio.read()
    # placeholder for STT engine
    text = "Recognized text from file"
    return {"text": text, "confidence": 0.95}

# ===== WebSocket: Real-Time Voice =====
@router.websocket("/stream/{user_id}")
async def voice_stream(websocket: WebSocket, user_id: str):
    if not user_id or user_id in ("undefined", "null"):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    logger.info(f"🎤 Voice connected | {user_id}")
    manager = voice_engine.get_manager(user_id)
    try:
        while True:
            pcm = await websocket.receive_bytes()
            result = manager.process_pcm(pcm)
            if result.get("partial"):
                await websocket.send_json({"type": "partial", "text": result["partial"]})
            if result.get("final"):
                await websocket.send_json({"type": "final", "text": result["final"]})
    except WebSocketDisconnect:
        logger.info(f"🔌 Voice disconnected | {user_id}")
    finally:
        voice_engine.cleanup(user_id)

# ===== REST: Audio Devices =====
@router.get("/devices")
async def get_audio_devices(user_id: str = Depends(get_current_user)):
    manager = voice_engine.get_manager(user_id)
    return {"devices": manager.get_available_devices()}
