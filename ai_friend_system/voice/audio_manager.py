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
from typing import Dict, Optional
from utils.logger import Logger
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from voice.pitch_analyzer import PitchAnalyzer


class AudioManager:
    """
    AudioManager uses shared singleton instances for STT/TTS to avoid loading models multiple times.
    Each AudioManager instance gets its own recognizer state but shares the model.
    """
    def __init__(self):
        self.logger = Logger("AudioManager")
        # Use singleton instances (models loaded once, shared)
        self.stt = SpeechToText()  # Singleton - model shared, recognizer per instance
        self.tts = TextToSpeech()  # Lightweight, can create new
        self.pitch_analyzer = PitchAnalyzer()  # Lightweight
        self.active = True
        self.is_speaking = False
        
        # Track pitch history for emotion detection
        self.pitch_history = []
        self.current_pitch = None

        self.logger.debug("🆕 AudioManager created (using shared STT model)")

    def initialize(self):
        self.logger.debug("🎧 AudioManager initialized")

    # ===============================
    # PCM STREAM → STT + PITCH ANALYSIS
    # ===============================
    def process_pcm(self, pcm_bytes: bytes) -> Dict:
        if not self.active:
            return {"partial": None, "final": None, "pitch": None}

        if self.is_speaking:
            return {"partial": None, "final": None, "pitch": None}

        # Analyze pitch in parallel (non-blocking)
        pitch_data = self.pitch_analyzer.analyze_pitch(pcm_bytes)
        if pitch_data["is_speech"] and pitch_data["pitch_hz"] > 0:
            self.current_pitch = pitch_data["pitch_hz"]
            self.pitch_history.append(pitch_data["pitch_hz"])
            if len(self.pitch_history) > 10:  # Keep last 10
                self.pitch_history.pop(0)
        
        # Process STT
        stt_result = self.stt.stream(pcm_bytes)
        
        # Add pitch data to result
        stt_result["pitch"] = pitch_data
        return stt_result

    # ===============================
    # TEXT → SPEECH (with emotion)
    # ===============================
    async def text_to_speech(self, text: str, emotion: str = "neutral", 
                            pitch_hint: Optional[float] = None) -> bytes:
        if not text:
            return b""

        self.is_speaking = True
        self.logger.debug(f"🗣️ TTS started | emotion={emotion}")

        try:
            # Use average pitch from history if no hint provided
            if pitch_hint is None and self.pitch_history:
                pitch_hint = sum(self.pitch_history) / len(self.pitch_history)
            
            audio = await self.tts.generate_audio_bytes(text, emotion, pitch_hint)
            self.logger.debug(f"🔊 TTS audio generated ({len(audio)} bytes)")
            return audio
        finally:
            self.is_speaking = False

    def reset(self):
        self.logger.debug("🔄 STT reset")
        self.stt.reset()
        self.pitch_history.clear()
        self.current_pitch = None

    def shutdown(self):
        self.logger.debug("🧹 AudioManager shutdown")
        self.active = False
        self.reset()
