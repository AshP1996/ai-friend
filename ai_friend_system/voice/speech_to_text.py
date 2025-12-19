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
from vosk import Model, KaldiRecognizer
from utils.logger import Logger


class SpeechToText:
    """
    Gemini-style Streaming Speech-To-Text
    -------------------------------------
    ✔ Real partial text
    ✔ Real final text
    ✔ Low latency
    ✔ Offline & free
    """

    def __init__(self):
        self.logger = Logger("SpeechToText")

        # 🔹 Load Vosk model
        self.model = Model("vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)

    # =====================================================
    # REAL-TIME PCM STREAMING (WebSocket)
    # =====================================================
    def stream(self, pcm: bytes) -> dict:
        """
        Receives 16-bit PCM @ 16kHz
        Returns partial + final results
        """

        if self.recognizer.AcceptWaveform(pcm):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()

            if text:
                self.logger.info(f"Final: {text}")
                return {"partial": None, "final": text}

            return {"partial": None, "final": None}

        else:
            result = json.loads(self.recognizer.PartialResult())
            partial = result.get("partial", "").strip()

            if partial:
                return {"partial": partial, "final": None}

            return {"partial": None, "final": None}

    # =====================================================
    # RESET (on disconnect)
    # =====================================================
    def reset(self):
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
