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
from .microphone_detector import MicrophoneDetector
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .audio_processor import AudioProcessor
from utils.logger import Logger
import asyncio

class AudioManager:
    def __init__(self):
        self.mic_detector = MicrophoneDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.processor = AudioProcessor()
        self.logger = Logger("AudioManager")
        self.is_listening = False
    
    def initialize(self) -> bool:
        devices = self.mic_detector.detect_microphones()
        if not devices:
            self.logger.error("No microphones found. Voice features disabled.")
            return False
        
        # Force correct device (fix)
        for d in devices:
            if "analog-stereo" in d["name"]:
                self.mic_detector.default_device = d
                break

        self.logger.info(f"Audio system initialized with {len(devices)} device(s)")
        return True
    
    async def listen(self, timeout: int = 15) -> Optional[str]:
        if self.is_listening:
            self.logger.warning("Already listening")
            return None
        
        self.is_listening = True
        try:
            device = self.mic_detector.get_default_device()

            # Debug log
            self.logger.info(f"Using microphone: {device}")

            text = await self.stt.listen_and_convert(device['index'], timeout)
            return text

        finally:
            self.is_listening = False
    
    async def speak(self, text: str):
        await self.tts.speak(text)
    
    def get_available_devices(self):
        return self.mic_detector.available_devices
