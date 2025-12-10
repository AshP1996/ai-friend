# import pyttsx3
# from typing import Optional
# from utils.logger import Logger
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from config import settings

# class TextToSpeech:
#     def __init__(self):
#         self.engine = None
#         self.logger = Logger("TextToSpeech")
#         self.executor = ThreadPoolExecutor(max_workers=1)
#         self._initialize_engine()
    
#     def _initialize_engine(self):
#         try:
#             self.engine = pyttsx3.init()
#             voice_config = settings.voice_config
            
#             # Set properties
#             self.engine.setProperty('rate', voice_config.get('tts_rate', 150))
#             self.engine.setProperty('volume', voice_config.get('tts_volume', 0.9))
            
#             # Try to set a pleasant voice
#             voices = self.engine.getProperty('voices')
#             if len(voices) > 1:
#                 self.engine.setProperty('voice', voices[1].id)
            
#             self.logger.info("TTS engine initialized")
#         except Exception as e:
#             self.logger.error(f"Error initializing TTS: {e}")
    
#     async def speak(self, text: str):
#         if not self.engine:
#             self.logger.error("TTS engine not initialized")
#             return
        
#         try:
#             loop = asyncio.get_event_loop()
#             await loop.run_in_executor(self.executor, self._blocking_speak, text)
#         except Exception as e:
#             self.logger.error(f"Error in TTS: {e}")
    
#     def _blocking_speak(self, text: str):
#         try:
#             self.logger.info(f"Speaking: {text[:50]}...")
#             self.engine.say(text)
#             self.engine.runAndWait()
#         except Exception as e:
#             self.logger.error(f"Error during speech: {e}")

import pyttsx3
from typing import Optional
from utils.logger import Logger
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import settings

class TextToSpeech:
    """
    Async Text-to-Speech using pyttsx3.
    Works offline and supports custom voice configuration.
    """

    def __init__(self):
        self.engine = None
        self.logger = Logger("TextToSpeech")
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._initialize_engine()

    def _initialize_engine(self):
        try:
            self.engine = pyttsx3.init()
            voice_config = getattr(settings, "voice_config", {})

            # Set rate and volume
            self.engine.setProperty('rate', voice_config.get('tts_rate', 150))
            self.engine.setProperty('volume', voice_config.get('tts_volume', 0.9))

            # Pick a pleasant voice
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)

            self.logger.info("TTS engine initialized")

        except Exception as e:
            self.logger.error(f"Error initializing TTS: {e}")

    async def speak(self, text: str):
        if not self.engine:
            self.logger.error("TTS engine not initialized")
            return

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self._blocking_speak, text)
        except Exception as e:
            self.logger.error(f"Error in TTS: {e}")

    def _blocking_speak(self, text: str):
        try:
            self.logger.info(f"Speaking: {text[:50]}...")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error during speech: {e}")
