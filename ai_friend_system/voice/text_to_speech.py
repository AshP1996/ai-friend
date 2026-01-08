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
from gtts import gTTS
from pydub import AudioSegment
from utils.logger import Logger


class TextToSpeech:
    def __init__(self):
        self.logger = Logger("TextToSpeech")
        self.logger.info("🆕 TextToSpeech initialized")

    async def generate_audio_bytes(self, text: str, emotion: str = "neutral") -> bytes:
        mp3_path = f"/tmp/{uuid.uuid4()}.mp3"
        wav_path = f"/tmp/{uuid.uuid4()}.wav"

        self.logger.info(f"🗣️ Generating speech | emotion={emotion}")
        self.logger.debug(f"📄 Text: {text}")

        try:
            def _generate():
                gTTS(text=text, lang="en").save(mp3_path)
                AudioSegment.from_mp3(mp3_path)\
                    .set_frame_rate(16000)\
                    .set_channels(1)\
                    .export(wav_path, format="wav")

            await asyncio.to_thread(_generate)

            with open(wav_path, "rb") as f:
                audio = f.read()

            self.logger.info(f"🔊 Audio ready ({len(audio)} bytes)")
            return audio

        finally:
            for p in (mp3_path, wav_path):
                if os.path.exists(p):
                    os.remove(p)
            self.logger.debug("🧹 Temp audio files cleaned")
