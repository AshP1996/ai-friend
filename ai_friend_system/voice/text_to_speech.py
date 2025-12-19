# import pyttsx3
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from utils.logger import Logger
# from .emotion_voice_map import EMOTION_VOICE_PROFILE

# class TextToSpeech:
#     def __init__(self):
#         self.engine = pyttsx3.init()
#         self.executor = ThreadPoolExecutor(max_workers=1)
#         self.is_speaking = False
#         self.logger = Logger("TextToSpeech")

#     async def speak(self, text: str, emotion: str = "neutral"):
#         if self.is_speaking:
#             self.stop()

#         profile = EMOTION_VOICE_PROFILE.get(
#             emotion, EMOTION_VOICE_PROFILE["neutral"]
#         )

#         self.is_speaking = True
#         loop = asyncio.get_event_loop()
#         await loop.run_in_executor(
#             self.executor, self._speak, text, profile
#         )
#         self.is_speaking = False

#     def stop(self):
#         try:
#             self.engine.stop()
#         except:
#             pass

#     def _speak(self, text: str, profile: dict):
#         self.engine.setProperty("rate", profile["rate"])
#         self.engine.setProperty("volume", profile["volume"])
#         self.engine.say(text)
#         self.engine.runAndWait()

import uuid
import asyncio
import os
from gtts import gTTS  # temporary neural-like TTS
from utils.logger import Logger

class TextToSpeech:
    def __init__(self):
        self.is_speaking = False
        self.logger = Logger("TextToSpeech")

    async def generate_to_file(self, text: str, emotion: str = "neutral") -> str:
        """
        Generate speech to a temporary file
        """
        path = f"/tmp/{uuid.uuid4()}.wav"

        def _generate():
            tts = gTTS(text=text, lang="en")
            tts.save(path)

        await asyncio.to_thread(_generate)
        self.logger.info(f"TTS generated: {path}")
        return path

    async def generate_audio_bytes(self, text: str, emotion: str = "neutral") -> bytes:
        """
        Generate speech and return audio bytes
        """
        path = await self.generate_to_file(text, emotion)
        with open(path, "rb") as f:
            audio_bytes = f.read()
        os.remove(path)
        return audio_bytes

    async def speak(self, text: str, emotion: str = "neutral"):
        """
        Gemini-style async TTS
        """
        self.is_speaking = True
        try:
            path = await self.generate_to_file(text, emotion)
            # You can integrate playback in frontend
        finally:
            self.is_speaking = False