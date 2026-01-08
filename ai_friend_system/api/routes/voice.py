# import asyncio
# import logging
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Depends
# from fastapi.responses import FileResponse

# from voice.audio_manager import AudioManager
# from .user import get_anonymous_user as get_current_user
# from core.session_manager import AIFriendSessions

# router = APIRouter()
# logger = logging.getLogger("VOICE")

# sessions = AIFriendSessions()


# # =====================================================
# # VOICE ENGINE (Per-user AudioManager)
# # =====================================================
# class VoiceEngine:
#     def __init__(self):
#         self._managers: dict[str, AudioManager] = {}
#         self._lock = asyncio.Lock()

#     async def get_manager(self, user_id: str) -> AudioManager:
#         async with self._lock:
#             manager = self._managers.get(user_id)

#             if manager is None:
#                 manager = AudioManager()
#                 manager.initialize()   # safe + useful
#                 self._managers[user_id] = manager

#             return manager

#     async def cleanup(self, user_id: str):
#         async with self._lock:
#             manager = self._managers.pop(user_id, None)

#         if manager:
#             try:
#                 manager.shutdown()
#             except Exception:
#                 logger.exception(
#                     f"Failed to shutdown AudioManager | {user_id}"
#                 )



# voice_engine = VoiceEngine()

# # =====================================================
# # REST: TEXT → SPEECH (OPTIONAL / DEBUG)
# # =====================================================
# @router.post("/tts")
# async def text_to_speech(
#     text: str,
#     emotion: str = "neutral",
#     user_id: str = Depends(get_current_user),
# ):
#     manager = await voice_engine.get_manager(user_id)
#     audio_bytes = await manager.text_to_speech(text, emotion)
#     return FileResponse(
#         content=audio_bytes,
#         media_type="audio/mpeg"
#     )


# # =====================================================
# # REST: FILE-BASED STT (OPTIONAL)
# # =====================================================
# @router.post("/stt")
# async def speech_to_text(
#     audio: UploadFile = File(...),
#     user_id: str = Depends(get_current_user),
# ):
#     manager = await voice_engine.get_manager(user_id)
#     audio_bytes = await audio.read()
#     result = manager.process_pcm(audio_bytes)
#     return {"text": result.get("final", "")}


# # =====================================================
# # WEBSOCKET: REAL-TIME VOICE (MAIN FEATURE)
# # =====================================================
# @router.websocket("/stream/{user_id}")
# async def voice_stream(websocket: WebSocket, user_id: str):
#     if not user_id or user_id in ("undefined", "null"):
#         await websocket.close(code=1008)
#         return

#     await websocket.accept()
#     logger.info(f"🎤 Voice connected | {user_id}")

#     manager = await voice_engine.get_manager(user_id)
#     session = await sessions.get_or_create(user_id)

#     loop = asyncio.get_running_loop()

#     try:
#         while True:
#             try:
#                 pcm_bytes = await asyncio.wait_for(
#                     websocket.receive_bytes(),
#                     timeout=30
#                 )
#             except asyncio.TimeoutError:
#                 await websocket.send_json({"type": "ping"})
#                 continue

#             # ===============================
#             # STT (run off event loop)
#             # ===============================
#             result = await loop.run_in_executor(
#                 None,
#                 manager.process_pcm,
#                 pcm_bytes
#             )

#             if result.get("partial"):
#                 await websocket.send_json({
#                     "type": "partial",
#                     "text": result["partial"]
#                 })

#             if result.get("final"):
#                 user_text = result["final"]

#                 # ===============================
#                 # AI CHAT
#                 # ===============================
#                 chat_result = await session.chat(user_text)
#                 ai_text = chat_result["response"]

#                 await websocket.send_json({
#                     "type": "final",
#                     "text": ai_text
#                 })

#                 # ===============================
#                 # TTS → BINARY FRAME
#                 # ===============================
#                 audio_bytes = await manager.text_to_speech(ai_text)
#                 await websocket.send_bytes(audio_bytes)

#     except WebSocketDisconnect:
#         logger.info(f"🔌 Voice disconnected | {user_id}")

#     except Exception as e:
#         logger.exception(f"Voice stream error | {user_id}: {e}")

#     finally:
#         await voice_engine.cleanup(user_id)
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Body
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel

from voice.audio_manager import AudioManager
from core.session_manager import AIFriendSessions
from agents.advanced_emotion_analyzer import AdvancedEmotionAnalyzer
from config import db_config

router = APIRouter()
logger = logging.getLogger("VOICE")

sessions = AIFriendSessions()
emotion_analyzer = AdvancedEmotionAnalyzer()


class VoiceEngine:
    def __init__(self):
        self._managers = {}
        self._lock = asyncio.Lock()

    async def get_manager(self, user_id: str) -> AudioManager:
        async with self._lock:
            if user_id not in self._managers:
                logger.debug(f"🆕 Creating AudioManager | user={user_id}")
                manager = AudioManager()
                manager.initialize()
                self._managers[user_id] = manager
            return self._managers[user_id]

    async def cleanup(self, user_id: str):
        async with self._lock:
            manager = self._managers.pop(user_id, None)
        if manager:
            logger.debug(f"🧹 Cleaning up AudioManager | user={user_id}")
            manager.shutdown()


voice_engine = VoiceEngine()


@router.websocket("/stream/{user_id}")
async def voice_stream(websocket: WebSocket, user_id: str):
    """Optimized real-time voice streaming with emotion detection and pitch analysis"""
    await websocket.accept()
    logger.info(f"🎤 Voice connected | user={user_id}")

    manager = await voice_engine.get_manager(user_id)
    session = await sessions.get_or_create(user_id)
    loop = asyncio.get_running_loop()
    
    # Track pitch history for emotion detection
    pitch_buffer = []

    try:
        await websocket.send_json({"type": "status", "state": "listening"})

        while True:
            # Receive message - handle both binary and JSON
            try:
                # Try to receive as bytes first (PCM audio)
                try:
                    pcm = await asyncio.wait_for(websocket.receive_bytes(), timeout=30.0)
                    
                    # Validate we got bytes
                    if not isinstance(pcm, bytes):
                        logger.warning(f"Received non-bytes: {type(pcm)}, skipping")
                        continue
                        
                    if len(pcm) == 0:
                        logger.debug("Received empty PCM chunk, skipping")
                        continue
                        
                except KeyError as ke:
                    # KeyError: 'bytes' means we received a JSON message instead
                    # This happens when frontend sends control messages
                    try:
                        data = await websocket.receive_json()
                        msg_type = data.get("type", "")
                        logger.debug(f"Received JSON message: {msg_type}")
                        
                        if msg_type in ("close", "disconnect"):
                            logger.info("Client requested disconnect")
                            break
                        elif msg_type == "ping":
                            await websocket.send_json({"type": "pong"})
                            continue
                        else:
                            # Unknown JSON message, skip and wait for PCM
                            continue
                    except Exception as json_e:
                        logger.debug(f"Could not parse as JSON: {json_e}, waiting for next message")
                        continue
                        
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                continue
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                error_msg = str(e)
                logger.error(f"WebSocket receive error: {e}", exc_info=True)
                # If it's a KeyError about bytes, try JSON
                if "bytes" in error_msg.lower() or isinstance(e, KeyError):
                    try:
                        data = await websocket.receive_json()
                        if data.get("type") in ("close", "disconnect"):
                            break
                        continue
                    except:
                        logger.error("Failed to handle message, closing connection")
                        break
                else:
                    break

            # Process PCM (STT + Pitch) in executor for speed
            try:
                result = await loop.run_in_executor(None, manager.process_pcm, pcm)
            except Exception as e:
                logger.error(f"Error processing PCM: {e}", exc_info=True)
                continue
            
            # Track pitch for emotion detection
            if result.get("pitch") and result["pitch"].get("is_speech"):
                pitch_data = result["pitch"]
                pitch_buffer.append(pitch_data)
                if len(pitch_buffer) > 20:  # Keep last 20 frames
                    pitch_buffer.pop(0)

            # Send partial transcription immediately
            if result.get("partial"):
                await websocket.send_json({
                    "type": "partial",
                    "text": result["partial"]
                })

            # Process final transcription
            if result.get("final"):
                user_text = result["final"]
                logger.info(f"🧑 User: {user_text}")

                # ADVANCED: Multi-modal emotion analysis (text + pitch + context)
                # Aggregate pitch data
                pitch_summary = None
                avg_pitch = 0.0
                avg_energy = 0.0
                pitch_emotion = "neutral"
                
                if pitch_buffer:
                    valid_pitches = [p["pitch_hz"] for p in pitch_buffer if p["pitch_hz"] > 0]
                    if valid_pitches:
                        avg_pitch = sum(valid_pitches) / len(valid_pitches)
                        avg_energy = sum(p.get("energy", 0) for p in pitch_buffer) / len(pitch_buffer)
                        avg_variation = sum(p.get("pitch_variation", 0) for p in pitch_buffer) / len(pitch_buffer)
                        
                        pitch_summary = {
                            "pitch_hz": avg_pitch,
                            "energy": avg_energy,
                            "pitch_variation": avg_variation,
                            "emotion_hint": pitch_buffer[-1].get("emotion_hint", "neutral")
                        }
                        
                        # Map pitch to emotion (enhanced)
                        if avg_pitch > 200 and avg_variation > 30:
                            pitch_emotion = "excited"
                        elif avg_pitch > 180:
                            pitch_emotion = "happy"
                        elif avg_pitch > 160:
                            pitch_emotion = "friendly"
                        elif avg_pitch < 120 and avg_energy < 0.05:
                            pitch_emotion = "sad"
                        elif avg_pitch < 140:
                            pitch_emotion = "calm"
                
                # Get conversation context for emotion analysis
                flow_context = session.ai_friend.flow_tracker.get_conversation_context() if hasattr(session.ai_friend, 'flow_tracker') else {}
                previous_emotion = flow_context.get('recent_emotions', [None])[-1] if flow_context.get('recent_emotions') else None
                
                # Advanced multi-modal emotion analysis
                emotion_context = {
                    'previous_emotion': previous_emotion,
                    'conversation_length': flow_context.get('conversation_length', 0)
                }
                
                text_emotion_task = emotion_analyzer.analyze(
                    user_text, 
                    context=emotion_context,
                    pitch_data=pitch_summary
                )
                
                # Wait for analysis
                text_emotion = await text_emotion_task
                final_emotion = text_emotion.get("primary_emotion", pitch_emotion)
                
                # Advanced fusion: Combine text and pitch with confidence weighting
                text_confidence = text_emotion.get("confidence", 0.5)
                pitch_confidence = 0.7 if pitch_summary and pitch_summary.get("pitch_hz", 0) > 0 else 0.3
                
                # Weighted decision
                if text_confidence > 0.6:
                    final_emotion = text_emotion.get("primary_emotion", final_emotion)
                elif pitch_confidence > 0.6 and pitch_emotion != "neutral":
                    final_emotion = pitch_emotion
                elif text_emotion.get("primary_emotion") == "neutral" and pitch_emotion != "neutral":
                    final_emotion = pitch_emotion
                
                logger.info(f"🎭 Emotion Analysis:")
                logger.info(f"   Text emotion: {text_emotion.get('primary_emotion')} (confidence: {text_confidence})")
                logger.info(f"   Pitch emotion: {pitch_emotion} (confidence: {pitch_confidence})")
                logger.info(f"   Final emotion: {final_emotion}")
                logger.info(f"   Intensity: {text_emotion.get('intensity_level', 'medium')}")

                manager.reset()
                
                # Save user message with voice data to database
                try:
                    async for db_session in db_config.get_session():
                        from database.models import MessageModel
                        from config.constants import MessageType
                        import json
                        
                        user_msg = MessageModel(
                            id=None,
                            conversation_id=session.ai_friend.conversation_id,
                            role=MessageType.USER,
                            content=user_text,
                            emotion=final_emotion,
                            voice_pitch=avg_pitch if avg_pitch > 0 else None,
                            voice_emotion=pitch_emotion if pitch_emotion != "neutral" else None,
                            audio_quality=avg_energy,
                            agent_outputs=json.dumps(text_emotion),
                            training_flag=True
                        )
                        await session.ai_friend.db_manager.save_message(db_session, user_msg)
                        await db_session.commit()
                except Exception as e:
                    logger.debug(f"Failed to save user message: {e}")
                
                pitch_buffer.clear()

                await websocket.send_json({
                    "type": "status",
                    "state": "thinking",
                    "text": user_text,
                    "emotion": final_emotion
                })

                # Generate response with emotion context (optimized, parallel)
                chat_task = session.chat(user_text)
                
                # Wait for response
                chat_result = await chat_task
                ai_text = chat_result["response"]
                
                # Extract emotion from response (multiple sources for best accuracy)
                emotion_data = chat_result.get("emotion", {})
                response_emotion = None
                
                if isinstance(emotion_data, dict):
                    # Try multiple keys
                    response_emotion = (
                        emotion_data.get("emotion") or 
                        emotion_data.get("primary_emotion") or
                        emotion_data.get("detected_emotion")
                    )
                
                # If no emotion from response metadata, analyze the AI's response text
                if not response_emotion or response_emotion == "neutral":
                    logger.info("🔍 Analyzing AI response text for emotion...")
                    ai_emotion_task = emotion_analyzer.analyze(ai_text)
                    ai_emotion_result = await ai_emotion_task
                    response_emotion = ai_emotion_result.get("primary_emotion") or ai_emotion_result.get("emotion")
                    logger.info(f"📊 Detected emotion from AI text: {response_emotion} (confidence: {ai_emotion_result.get('confidence', 0)})")
                
                # Fallback to user's emotion if still neutral or missing
                if not response_emotion or response_emotion == "neutral":
                    response_emotion = final_emotion
                    logger.info(f"🔄 Using user's emotion as fallback: {response_emotion}")
                
                # Ensure we have a valid emotion
                valid_emotions = ["happy", "excited", "sad", "neutral", "angry", "calm", "friendly"]
                if response_emotion not in valid_emotions:
                    # Map to closest valid emotion
                    if any(word in response_emotion.lower() for word in ["happy", "joy", "glad", "great"]):
                        response_emotion = "happy"
                    elif any(word in response_emotion.lower() for word in ["excited", "wow", "amazing"]):
                        response_emotion = "excited"
                    elif any(word in response_emotion.lower() for word in ["sad", "sorry", "unfortunate"]):
                        response_emotion = "sad"
                    else:
                        response_emotion = "friendly"  # Default to friendly instead of neutral
                
                logger.info(f"🤖 AI Response: {ai_text[:80]}...")
                logger.info(f"🎭 Final emotion for TTS: {response_emotion}")

                # Send response text immediately (BOTH text and voice will be sent)
                await websocket.send_json({
                    "type": "response",
                    "text": ai_text,
                    "emotion": response_emotion,
                    "has_audio": True  # Indicate audio is coming
                })

                # Send status before generating audio
                await websocket.send_json({
                    "type": "status",
                    "state": "speaking"
                })
                
                try:
                    # Generate TTS with emotion and pitch matching
                    logger.info(f"🎤 Generating TTS with emotion:")
                    logger.info(f"   Text: {ai_text[:100]}...")
                    logger.info(f"   Emotion: {response_emotion}")
                    logger.info(f"   Pitch hint: {avg_pitch if avg_pitch > 0 else 'None'}")
                    
                    audio = await manager.text_to_speech(
                        ai_text, 
                        emotion=response_emotion,
                        pitch_hint=avg_pitch if avg_pitch > 0 else None
                    )
                    
                    logger.info(f"✅ TTS generated with emotion '{response_emotion}' ({len(audio) if audio else 0} bytes)")
                    
                    # Validate audio is bytes
                    if audio is None:
                        logger.warning("⚠️ TTS returned None")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Audio generation returned None"
                        })
                    elif not isinstance(audio, bytes):
                        logger.error(f"⚠️ TTS returned wrong type: {type(audio)}, value: {audio}")
                        # Try to convert to bytes
                        try:
                            if isinstance(audio, (bytearray, memoryview)):
                                audio = bytes(audio)
                            elif hasattr(audio, 'read'):
                                audio = audio.read()
                            else:
                                raise TypeError(f"Cannot convert {type(audio)} to bytes")
                            logger.info(f"✅ Converted audio to bytes: {len(audio)} bytes")
                        except Exception as conv_e:
                            logger.error(f"❌ Failed to convert audio to bytes: {conv_e}")
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Audio type conversion failed: {str(conv_e)}"
                            })
                            continue
                    
                    if len(audio) == 0:
                        logger.warning("⚠️ TTS generated empty audio")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Audio generation failed (empty)"
                        })
                    else:
                        logger.info(f"🔊 Audio generated ({len(audio)} bytes), sending in chunks...")
                        
                        # Send audio start message
                        await websocket.send_json({
                            "type": "audio_start",
                            "size": len(audio),
                            "format": "wav"
                        })
                        
                        # Send audio in chunks for streaming (reduces latency)
                        chunk_size = 4096
                        total_chunks = (len(audio) + chunk_size - 1) // chunk_size
                        
                        for i in range(0, len(audio), chunk_size):
                            chunk = audio[i:i+chunk_size]
                            # Double-check chunk is bytes
                            if not isinstance(chunk, bytes):
                                chunk = bytes(chunk)
                            await websocket.send_bytes(chunk)
                            logger.debug(f"📤 Sent audio chunk {i//chunk_size + 1}/{total_chunks} ({len(chunk)} bytes)")
                        
                        # Send audio end message
                        await websocket.send_json({
                            "type": "audio_end",
                            "total_bytes": len(audio)
                        })
                        
                        logger.info(f"✅ Audio sent successfully ({len(audio)} bytes total)")
                
                except Exception as e:
                    logger.error(f"❌ TTS generation error: {e}", exc_info=True)
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Audio generation failed: {str(e)}"
                    })

                # Mark speaking complete
                await websocket.send_json({
                    "type": "status",
                    "state": "listening"
                })
                
                logger.debug("✅ Voice response complete (text + audio)")

    except WebSocketDisconnect:
        logger.info(f"🔌 Voice disconnected | user={user_id}")

    except Exception as e:
        logger.error(f"❌ Voice error | user={user_id}: {e}")

    finally:
        await voice_engine.cleanup(user_id)


# =====================================================
# REST: TEXT → SPEECH (for frontend TTS requests)
# Supports both GET (query params) and POST (body)
# =====================================================

class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "default"
    emotion: Optional[str] = "neutral"

@router.get("/tts")
async def text_to_speech_get(
    text: str = Query(..., description="Text to convert to speech"),
    voice_id: str = Query("default", description="Voice ID"),
    emotion: str = Query("neutral", description="Emotion for voice synthesis")
):
    """Generate TTS audio from text (GET)"""
    return await _generate_tts(text, emotion)

@router.post("/tts")
async def text_to_speech_post(
    request: TTSRequest = Body(...)
):
    """Generate TTS audio from text (POST)"""
    return await _generate_tts(request.text, request.emotion or "neutral")

async def _generate_tts(text: str, emotion: str = "neutral"):
    """Internal function to generate TTS audio"""
    try:
        if not text:
            return Response(
                content="Missing 'text' parameter",
                status_code=400,
                media_type="text/plain"
            )
        
        logger.info(f"🎤 TTS request | text_length={len(text)}, emotion={emotion}")
        
        # Get a temporary manager for TTS
        manager = AudioManager()
        manager.initialize()
        
        # Generate audio
        audio_bytes = await manager.text_to_speech(text, emotion=emotion)
        
        # Validate audio is bytes
        if audio_bytes is None:
            logger.warning("⚠️ TTS returned None")
            return Response(
                content="Audio generation returned None",
                status_code=500,
                media_type="text/plain"
            )
        
        if not isinstance(audio_bytes, bytes):
            logger.error(f"⚠️ TTS returned wrong type: {type(audio_bytes)}")
            try:
                if isinstance(audio_bytes, (bytearray, memoryview)):
                    audio_bytes = bytes(audio_bytes)
                elif hasattr(audio_bytes, 'read'):
                    audio_bytes = audio_bytes.read()
                else:
                    return Response(
                        content=f"Audio type error: {type(audio_bytes)}",
                        status_code=500,
                        media_type="text/plain"
                    )
            except Exception as conv_e:
                logger.error(f"❌ Failed to convert audio to bytes: {conv_e}")
                return Response(
                    content=f"Audio conversion failed: {str(conv_e)}",
                    status_code=500,
                    media_type="text/plain"
                )
        
        if len(audio_bytes) == 0:
            logger.warning("⚠️ TTS generated empty audio")
            return Response(
                content="Audio generation failed (empty)",
                status_code=500,
                media_type="text/plain"
            )
        
        logger.info(f"✅ TTS generated {len(audio_bytes)} bytes")
        
        # Return audio as WAV
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=tts_output.wav",
                "Content-Length": str(len(audio_bytes))
            }
        )
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response(
            content=f"TTS error: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )
