# # voice/speech_to_text.py
# import speech_recognition as sr
# from utils.logger import Logger
# import webrtcvad
# import asyncio

# class SpeechToText:
#     def __init__(self):
#         self.recognizer = sr.Recognizer()
#         self.logger = Logger("SpeechToText")
#         self.buffer = b""
#         self.partial_text = ""
#         self.vad = webrtcvad.Vad(2)  # aggressive VAD
#         self.sample_rate = 16000
#         self.chunk_size = 320  # 20ms

#     # ===== REAL-TIME PCM STREAM =====
#     def stream(self, pcm: bytes) -> dict:
#         self.buffer += pcm
#         # Fake partial every second
#         if len(self.buffer) > 16000 * 2:
#             self.partial_text += " ..."
#             return {"partial": self.partial_text, "final": None}

#         # Fake final after 6 sec
#         if len(self.buffer) > 16000 * 6:
#             final = "Hello, this is the final text."
#             self.buffer = b""
#             self.partial_text = ""
#             return {"partial": None, "final": final}

#         return {"partial": None, "final": None}

#     async def listen_and_convert(self, device_index: int, timeout: int = 5) -> str | None:
#         try:
#             mic = sr.Microphone(device_index=device_index, sample_rate=self.sample_rate)
#             with mic as source:
#                 self.logger.info("Listening...")
#                 self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
#                 audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
#             text = self.recognizer.recognize_google(audio, language="en-IN")
#             self.logger.info(f"Recognized: {text}")
#             return text
#         except (sr.WaitTimeoutError, sr.UnknownValueError):
#             return None
#         except Exception as e:
#             self.logger.error(f"STT listen error: {e}")
#             return None

#     def reset(self):
#         self.buffer = b""
#         self.partial_text = ""
#         self.recognizer = sr.Recognizer()
import json
import time
import numpy as np
from vosk import Model, KaldiRecognizer
from utils.logger import Logger
import threading


class SpeechToText:
    """
    Streaming STT (Vosk) with silence detection for final transcription
    PCM: 16-bit, 16kHz, mono
    
    SHARED MODEL: Vosk model is loaded once and shared across all instances.
    Each instance gets its own recognizer for thread safety.
    """
    _model = None
    _lock = threading.Lock()
    _logger = Logger("SpeechToText")
    _model_loaded = False

    def __init__(self):
        self.logger = self.__class__._logger
        
        # Load model only once (shared across all instances)
        if not self.__class__._model_loaded:
            with self.__class__._lock:
                if not self.__class__._model_loaded:
                    self.logger.info("🧠 Loading Vosk model (shared, one-time load)...")
                    self.__class__._model = Model("vosk-model-small-en-us-0.15")
                    self.__class__._model_loaded = True
                    self.logger.info("✅ Vosk model loaded (will be shared across all instances)")
        
        # Use shared model, but create own recognizer per instance
        self.model = self.__class__._model
        self._create_recognizer()
        
        # Per-instance state (each user gets their own recognizer and state)
        self.silence_threshold = 0.01
        self.silence_duration = 1.0
        self.last_speech_time = time.time()
        self.last_partial_text = ""
        self.buffer_audio = b""
        self.buffer_duration = 0.0
        
        self.logger.debug("✅ STT instance ready (using shared model, own recognizer)")

    def _create_recognizer(self):
        """Create a new recognizer for this instance (thread-safe per user)"""
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        self.logger.debug("🔁 Recognizer created (per-instance, shared model)")

    def _detect_silence(self, pcm: bytes) -> bool:
        """Detect if audio chunk is silence"""
        try:
            # Convert to numpy array
            audio_data = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0
            
            # Calculate energy
            energy = np.mean(np.abs(audio_data))
            return energy < self.silence_threshold
        except Exception as e:
            self.logger.debug(f"Silence detection error: {e}")
            return False

    def stream(self, pcm: bytes) -> dict:
        """Process PCM audio with silence detection for final transcription"""
        current_time = time.time()
        
        # Check if we have a final result from Vosk (natural utterance end)
        if self.recognizer.AcceptWaveform(pcm):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()

            if text:
                self.logger.info(f"📝 FINAL STT (Vosk): {text}")
                self._reset_tracking()
                return {"partial": None, "final": text}

        # Get partial result
        partial_result = json.loads(self.recognizer.PartialResult())
        partial_text = partial_result.get("partial", "").strip()
        
        # Check for silence in current chunk
        is_silent = self._detect_silence(pcm)
        
        # Update tracking based on speech/silence
        if partial_text:
            # We have speech - update last speech time
            self.last_speech_time = current_time
            self.last_partial_text = partial_text
            self.buffer_duration = 0.0
        elif is_silent and self.last_partial_text:
            # We have silence and previous speech - accumulate silence
            self.buffer_duration += len(pcm) / 16000.0  # Approximate duration in seconds
        
        # Check if we should return final based on silence duration
        silence_elapsed = current_time - self.last_speech_time
        
        # Return final if we have text and sufficient silence
        if self.last_partial_text and silence_elapsed >= self.silence_duration:
            final_text = self.last_partial_text
            self.logger.info(f"📝 FINAL STT (silence {silence_elapsed:.2f}s): {final_text}")
            self._reset_tracking()
            return {"partial": None, "final": final_text}
        
        # Return partial if available
        if partial_text:
            self.logger.debug(f"✏️ PARTIAL STT: {partial_text}")
            return {"partial": partial_text, "final": None}

        return {"partial": None, "final": None}
    
    def _reset_tracking(self):
        """Reset silence detection tracking"""
        self.last_speech_time = time.time()
        self.last_partial_text = ""
        self.buffer_audio = b""
        self.buffer_duration = 0.0

    def reset(self):
        """Reset recognizer and tracking"""
        self.logger.info("🔄 Resetting recognizer")
        self._create_recognizer()
        self._reset_tracking()