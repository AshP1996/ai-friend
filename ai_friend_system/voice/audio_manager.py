# from typing import Optional
# from .microphone_detector import MicrophoneDetector
# from .speech_to_text import SpeechToText
# from .text_to_speech import TextToSpeech
# from .audio_processor import AudioProcessor
# from utils.logger import Logger
# import asyncio

# class AudioManager:
#     def __init__(self):
#         self.mic_detector = MicrophoneDetector()
#         self.stt = SpeechToText()
#         self.tts = TextToSpeech()
#         self.processor = AudioProcessor()
#         self.logger = Logger("AudioManager")
#         self.is_listening = False
    
#     def initialize(self) -> bool:
#         devices = self.mic_detector.detect_microphones()
#         if not devices:
#             self.logger.error("No microphones found. Voice features disabled.")
#             return False
        
#         self.logger.info(f"Audio system initialized with {len(devices)} device(s)")
#         return True
    
#     async def listen(self, timeout: int = 5) -> Optional[str]:
#         if self.is_listening:
#             self.logger.warning("Already listening")
#             return None
        
#         self.is_listening = True
#         try:
#             device = self.mic_detector.get_default_device()
#             if not device:
#                 return None
            
#             text = await self.stt.listen_and_convert(device['index'], timeout)
#             return text
#         finally:
#             self.is_listening = False
    
#     async def speak(self, text: str):
#         await self.tts.speak(text)
    
#     def get_available_devices(self):
#         return self.mic_detector.available_devices

from typing import Optional
import asyncio

from .microphone_detector import MicrophoneDetector
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .audio_processor import AudioProcessor
from utils.logger import Logger


class AudioManager:
    """
    Central audio controller

    Responsibilities:
    - Microphone detection
    - Speech-to-text
    - Text-to-speech
    - Safe async voice handling
    """

    def __init__(self):
        self.mic_detector = MicrophoneDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.processor = AudioProcessor()
        self.logger = Logger("AudioManager")

        self.is_listening: bool = False
        self.initialized: bool = False

    # =====================================================
    # INIT
    # =====================================================
    def initialize(self) -> bool:
        devices = self.mic_detector.detect_microphones()
        if not devices:
            self.logger.error("No microphones found. Voice features disabled.")
            return False

        # Prefer analog device if available (Linux fix)
        for d in devices:
            if "analog" in d["name"].lower():
                self.mic_detector.default_device = d
                break

        self.initialized = True
        self.logger.info(f"Audio system initialized with {len(devices)} device(s)")
        return True

    # =====================================================
    # LISTEN
    # =====================================================
    async def listen(self, timeout: Optional[int] = 5) -> Optional[str]:
        """
        Listen to microphone and convert speech to text

        :param timeout: max seconds to listen
        """

        if not self.initialized:
            self.logger.warning("AudioManager not initialized")
            return None

        if self.is_listening:
            self.logger.warning("Already listening, skipping")
            return None

        self.is_listening = True

        try:
            device = self.mic_detector.get_default_device()
            if not device:
                self.logger.error("No default microphone device")
                return None

            self.logger.info("🎤 Listening...")

            text = await asyncio.wait_for(
                self.stt.listen_and_convert(
                    device_index=device["index"],
                    timeout=timeout
                ),
                timeout=(timeout + 1) if timeout else None
            )

            if text:
                self.logger.info(f"🗣️ Transcribed: {text}")

            return text

        except asyncio.TimeoutError:
            self.logger.info("Listening timeout reached")
            return None

        except Exception as e:
            self.logger.error(f"Audio listen failed: {e}")
            return None

        finally:
            self.is_listening = False

    # =====================================================
    # SPEAK
    # =====================================================
    async def speak(self, text: str, emotion: str = "neutral"):
        """
        Convert text to speech
        """
        if not self.initialized:
            self.logger.warning("AudioManager not initialized")
            return

        if not text:
            return

        try:
            self.logger.info("🔊 Speaking...")
            await self.tts.speak(text, emotion)
        except Exception as e:
            self.logger.error(f"TTS failed: {e}")

    # =====================================================
    # STREAMING (FUTURE)
    # =====================================================
    def process_pcm(self, pcm_bytes: bytes):
        """
        Process streaming PCM chunks (WebSocket / realtime)
        """
        return self.stt.stream(pcm_bytes)

    # =====================================================
    # SHUTDOWN
    # =====================================================
    def shutdown(self):
        self.logger.info("Shutting down audio system")
        self.stt.reset()
        self.initialized = False

    # =====================================================
    # DEVICES
    # =====================================================
    def get_available_devices(self):
        return self.mic_detector.available_devices
