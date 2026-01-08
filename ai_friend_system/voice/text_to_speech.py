# import uuid
# import asyncio
# import os
# from gtts import gTTS
# from utils.logger import Logger


# class TextToSpeech:
#     """
#     Async TTS
#     Returns audio bytes (MP3)
#     """

#     def __init__(self):
#         self.logger = Logger("TextToSpeech")
#         self.is_speaking = False

#     async def generate_audio_bytes(self, text: str, emotion: str = "neutral") -> bytes:
#         self.is_speaking = True
#         path = f"/tmp/{uuid.uuid4()}.mp3"

#         try:
#             def _generate():
#                 gTTS(text=text, lang="en").save(path)

#             await asyncio.to_thread(_generate)

#             with open(path, "rb") as f:
#                 audio = f.read()

#             return audio

#         finally:
#             self.is_speaking = False
#             if os.path.exists(path):
#                 os.remove(path)
import uuid
import asyncio
import os
from utils.logger import Logger
from .emotion_voice_synthesizer import EmotionVoiceSynthesizer

class TextToSpeech:
    def __init__(self):
        self.logger = Logger("TextToSpeech")
        self.synthesizer = EmotionVoiceSynthesizer()
        self.logger.debug("🆕 TextToSpeech initialized with emotion synthesis")

    async def generate_audio_bytes(self, text: str, emotion: str = "neutral", 
                                   pitch_hint: float = None) -> bytes:
        """Generate emotion-aware, human-like speech"""
        self.logger.debug(f"🗣️ Generating speech | emotion={emotion}, pitch={pitch_hint}")
        
        # Use emotion-aware synthesizer
        audio = await self.synthesizer.synthesize(text, emotion, pitch_hint)
        
        self.logger.debug(f"🔊 Audio ready ({len(audio)} bytes)")
        return audio
