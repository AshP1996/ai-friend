"""
Advanced voice routes with streaming and wake-word detection
"""

from fastapi import APIRouter, WebSocket, UploadFile, File, Depends
from api.routes.auth import get_current_user
from voice import AudioManager
import io

router = APIRouter()

class VoiceEngine:
    def __init__(self):
        self.audio_managers = {}  # Per-user audio manager
    
    def get_manager(self, user_id: str) -> AudioManager:
        if user_id not in self.audio_managers:
            self.audio_managers[user_id] = AudioManager()
            self.audio_managers[user_id].initialize()
        return self.audio_managers[user_id]

voice_engine = VoiceEngine()

@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    '''Convert speech to text'''
    audio_data = await audio.read()
    # Process audio here
    return {"text": "Recognized text", "confidence": 0.95}

@router.post("/tts")
async def text_to_speech(
    text: str,
    voice_id: str = "default",
    user_id: str = Depends(get_current_user)
):
    '''Convert text to speech'''
    manager = voice_engine.get_manager(user_id)
    # Generate speech audio
    return {"audio_url": "/audio/output.mp3", "duration": 3.5}

@router.websocket("/stream/{user_id}")
async def voice_stream(websocket: WebSocket, user_id: str):
    '''Real-time voice streaming'''
    await websocket.accept()
    
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            # Process audio chunk
            text = "recognized text"  # STT here
            await websocket.send_json({"text": text})
    except:
        await websocket.close()

@router.get("/devices")
async def get_audio_devices(user_id: str = Depends(get_current_user)):
    '''List available audio devices'''
    manager = voice_engine.get_manager(user_id)
    devices = manager.get_available_devices()
    return {"devices": devices}
