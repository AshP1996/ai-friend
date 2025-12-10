# import speech_recognition as sr
# from typing import Optional
# from utils.logger import Logger
# import asyncio
# from concurrent.futures import ThreadPoolExecutor

# class SpeechToText:
#     def __init__(self):
#         self.recognizer = sr.Recognizer()
#         self.logger = Logger("SpeechToText")
#         self.executor = ThreadPoolExecutor(max_workers=1)
        
#         # Optimize recognizer settings
#         self.recognizer.energy_threshold = 4000
#         self.recognizer.dynamic_energy_threshold = True
#         self.recognizer.pause_threshold = 0.8
    
#     async def listen_and_convert(self, device_index: Optional[int] = None, timeout: int = 5) -> Optional[str]:
#         try:
#             loop = asyncio.get_event_loop()
#             text = await loop.run_in_executor(
#                 self.executor,
#                 self._blocking_listen,
#                 device_index,
#                 timeout
#             )
#             return text
#         except Exception as e:
#             self.logger.error(f"Error in speech recognition: {e}")
#             return None
    
#     def _blocking_listen(self, device_index: Optional[int], timeout: int) -> Optional[str]:
#         try:
#             with sr.Microphone(device_index=device_index) as source:
#                 self.logger.info("Listening...")
#                 self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
#                 audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                
#                 self.logger.info("Processing speech...")
#                 text = self.recognizer.recognize_google(audio)
#                 self.logger.info(f"Recognized: {text}")
#                 return text
#         except sr.WaitTimeoutError:
#             self.logger.warning("Listening timeout")
#             return None
#         except sr.UnknownValueError:
#             self.logger.warning("Could not understand audio")
#             return None
#         except sr.RequestError as e:
#             self.logger.error(f"Recognition service error: {e}")
#             return None
#         except Exception as e:
#             self.logger.error(f"Unexpected error: {e}")
#             return None


import speech_recognition as sr
from typing import Optional
from utils.logger import Logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

class SpeechToText:
    """
    Async Speech-to-Text using Google Web Speech API.
    Optimized for Linux/Ubuntu microphones.
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.logger = Logger("SpeechToText")
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Adjust for Ubuntu laptop mics
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.3

    async def listen_and_convert(
        self, device_index: Optional[int] = None, timeout: int = 8
    ) -> Optional[str]:
        """
        Async wrapper for blocking microphone input.
        """
        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor,
                self._blocking_listen,
                device_index,
                timeout
            )
            return text
        except Exception as e:
            self.logger.error(f"Error in STT: {e}")
            return None

    def _blocking_listen(self, device_index: Optional[int], timeout: int) -> Optional[str]:
        try:
            with sr.Microphone(device_index=device_index, sample_rate=44100) as source:
                self.logger.info(f"Listening on device {device_index}...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.2)

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=20
                )

                self.logger.info("Processing speech...")
                text = self.recognizer.recognize_google(audio, language="en-IN")
                self.logger.info(f"Recognized text: {text}")
                return text

        except sr.WaitTimeoutError:
            self.logger.warning("Timeout: No speech detected")
            return None

        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return None

        except sr.RequestError as e:
            self.logger.error(f"Google API Error: {e}")
            return None

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
