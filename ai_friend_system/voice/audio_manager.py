# class AudioManager:
#     """
#     Central Voice Controller
#     - Receives PCM stream
#     - Produces partial & final STT
#     - Generates TTS audio bytes
#     """

#     def __init__(self):
#         self.logger = Logger("AudioManager")
#         self.stt = SpeechToText()
#         self.tts = TextToSpeech()
#         self.active = True

#     # ✅ ADD THIS
#     def initialize(self):
#         """
#         Compatibility init hook.
#         Streaming STT initializes lazily.
#         """
#         self.logger.info("🎧 AudioManager initialized")

#     # ===============================
#     # PCM STREAM (WebSocket)
#     # ===============================
#     # def process_pcm(self, pcm_bytes: bytes) -> Dict:
#     #     self.logger.info(f"🎧 PCM chunk received: {len(pcm_bytes)} bytes")

#     #     if not self.active:
#     #         return {"partial": None, "final": None}

#     #     return self.stt.stream(pcm_bytes)

#     def process_pcm(self, pcm_bytes: bytes) -> Dict:
#         self.logger.warning(f"🎧 PCM RECEIVED: {len(pcm_bytes)} bytes")
#         return self.stt.stream(pcm_bytes)
#     # ===============================
#     # TEXT → SPEECH
#     # ===============================
#     async def text_to_speech(self, text: str, emotion: str = "neutral") -> bytes:
#         if not text:
#             return b""

#         return await self.tts.generate_audio_bytes(text, emotion)

#     # ===============================
#     # RESET / SHUTDOWN
#     # ===============================
#     def reset(self):
#         self.stt.reset()

#     def shutdown(self):
#         self.active = False
#         self.reset()
from typing import Dict
from utils.logger import Logger
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech


class AudioManager:
    def __init__(self):
        self.logger = Logger("AudioManager")
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.active = True
        self.is_speaking = False

        self.logger.info("🆕 AudioManager created")

    def initialize(self):
        self.logger.info("🎧 AudioManager initialized")

    # ===============================
    # PCM STREAM → STT
    # ===============================
    def process_pcm(self, pcm_bytes: bytes) -> Dict:
        if not self.active:
            self.logger.warning("⛔ Ignoring PCM: manager inactive")
            return {"partial": None, "final": None}

        if self.is_speaking:
            self.logger.debug("🔇 Ignoring PCM: AI is speaking")
            return {"partial": None, "final": None}

        self.logger.debug(f"🎙️ PCM received: {len(pcm_bytes)} bytes")
        return self.stt.stream(pcm_bytes)

    # ===============================
    # TEXT → SPEECH
    # ===============================
    async def text_to_speech(self, text: str, emotion: str = "neutral") -> bytes:
        if not text:
            self.logger.warning("⚠️ Empty TTS request")
            return b""

        self.is_speaking = True
        self.logger.info(f"🗣️ TTS started | emotion={emotion}")

        try:
            audio = await self.tts.generate_audio_bytes(text, emotion)
            self.logger.info(f"🔊 TTS audio generated ({len(audio)} bytes)")
            return audio
        finally:
            self.is_speaking = False
            self.logger.info("🎧 TTS finished, listening resumed")

    def reset(self):
        self.logger.info("🔄 STT reset")
        self.stt.reset()

    def shutdown(self):
        self.logger.info("🧹 AudioManager shutdown")
        self.active = False
        self.reset()
