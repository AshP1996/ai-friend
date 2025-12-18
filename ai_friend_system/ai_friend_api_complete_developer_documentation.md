# 🤖 AI FRIEND API – COMPLETE DEVELOPER DOCUMENTATION

Version: **2.0.0**  
Base URL: `http://127.0.0.1:8000`

---

## 📌 OVERVIEW

AI Friend API is a **modular, production‑ready conversational AI platform** that provides:

- Intelligent chat (local + cloud LLMs)
- Emotion analysis
- Semantic memory
- Voice (STT / TTS)
- Streaming responses (ChatGPT‑like)
- Analytics & insights
- Persona & avatar control
- Multi‑session support (no auth required)

All APIs are **REST‑based**, with optional **WebSocket & SSE streaming**.

---

## 🧠 SESSION & USER MODEL

- Authentication: ❌ **Disabled**
- User ID: Auto‑generated (`guest-uuid`)
- Sessions: In‑memory session manager
- Session timeout: Configurable (default 30 min)

Each request automatically maps to a session.

---

# 💬 CHAT APIS

## 1️⃣ Send Message

**POST** `/api/chat/send`

Full AI processing pipeline:
- Emotion detection
- Memory retrieval
- LLM response generation
- Optional memory saving

### Request Body
```json
{
  "message": "Hello tell me a joke",
  "context": {"greeting": "hello"},
  "save_to_memory": true
}
```

### Response
```json
{
  "response": "Sure! Why did the computer laugh?...",
  "emotion": {
    "primary_emotion": "neutral",
    "confidence": 0.5,
    "sentiment_score": 0,
    "intensity": "low"
  },
  "processing_time": 3.86,
  "memories_used": 0,
  "session_id": "uuid"
}
```

### Notes
- Uses Ollama → HuggingFace → Cloud → Rule‑based fallback
- Saves memory only if emotion confidence > 0.6

---

## 2️⃣ Streaming Chat (ChatGPT‑style)

**GET** `/api/chat/stream?message=Hi`

- Uses **Server‑Sent Events (SSE)**
- Streams word‑by‑word

### Response (SSE)
```
event: message
data: Hi!

event: message
data: Hope

event: done
data: complete
```

### Use Case
- Web UI typing animation
- Real‑time assistant feel

---

## 3️⃣ Chat History

**GET** `/api/chat/history?limit=10`

Returns session summary (not raw messages).

```json
{
  "conversation_id": 16,
  "session_id": "uuid",
  "user_id": "guest-uuid",
  "stats": {
    "message_count": 0,
    "avg_processing_time": 0
  }
}
```

---

## 4️⃣ Clear Conversation

**DELETE** `/api/chat/clear`

Clears session + memory context.

```json
{"message": "Conversation cleared"}
```

---

# 🧠 MEMORY APIS

## 5️⃣ Save Memory

**POST** `/api/memory/save`

```json
{
  "content": "hello",
  "category": "general",
  "importance": 0.5,
  "tags": "greeting"
}
```

⚠️ **Important**: `tags` must NOT be a list. Use string or null.

---

## 6️⃣ Search Memories

**POST** `/api/memory/search`

```json
{
  "query": "hello",
  "limit": 10,
  "category": "general"
}
```

Response:
```json
{
  "memories": [],
  "count": 0
}
```

---

## 7️⃣ Delete Memory

**DELETE** `/api/memory/{memory_id}`

---

## 8️⃣ Memory Stats

**GET** `/api/memory/stats`

---

# 🎙️ VOICE APIS

## 9️⃣ Speech‑to‑Text (STT)

**POST** `/api/voice/stt`

- Multipart upload
- Audio / Video supported

```bash
-F audio=@file.mp4
```

Response:
```json
{
  "text": "Recognized text",
  "confidence": 0.95
}
```

---

## 🔊 Text‑to‑Speech (TTS)

**POST** `/api/voice/tts?text=hello&emotion=neutral`

```json
{"status": "speaking"}
```

---

## 🎧 Audio Devices

**GET** `/api/voice/devices`

Returns all system audio devices.

---

# 👤 PROFILE APIS

- **GET** `/api/profile/{user_id}`
- **PUT** `/api/profile/{user_id}`

Stores preferences, persona overrides, metadata.

---

# 🤖 AGENTS

## Agent Status

**GET** `/api/agents/status`

```json
{
  "agents": [
    {"type": "emotion", "status": "active"}
  ]
}
```

---

# 📊 ANALYTICS

## Overview

**GET** `/api/analytics/overview`

Includes:
- Total interactions
- Emotion distribution
- Topics
- Memory stats

---

## Emotion Trends

**GET** `/api/analytics/emotion-trends?days=7`

---

## Topic Analysis

**GET** `/api/analytics/topics`

---

# 🎭 PERSONA APIS

## Get Persona

**GET** `/api/persona/get`

```json
{
  "name": "Friend",
  "personality_traits": {
    "empathy": 0.9
  }
}
```

---

## Update Persona

**POST** `/api/persona/update`

---

## Reset Persona

**POST** `/api/persona/reset`

---

# 🧍 AVATAR APIS

## Expression Control

**POST** `/api/avatar/expression`

```json
{
  "emotion": "Angry",
  "intensity": 0.8,
  "duration": 2
}
```

---

## Animation

**POST** `/api/avatar/animation`

---

## Lip‑Sync Data

**GET** `/api/avatar/sync-speech?text=hi friend`

Returns phoneme timing for 3D avatars.

---

# ⚙️ SYSTEM APIS

## Root

**GET** `/`

Returns API metadata.

---

## Health Check

**GET** `/health`

---

## System Stats

**GET** `/stats`

```json
{"active_sessions": 0}
```

---

# 🧪 ERROR HANDLING

| Code | Meaning |
|----|----|
| 200 | Success |
| 422 | Validation Error |
| 500 | Internal Error |

---

# 🚀 BEST PRACTICES

- Use `/chat/stream` for UI
- Save memories selectively
- Use persona for tone control
- Avatar APIs for immersive UX

---

# ✅ READY FOR

- Web apps
- Mobile apps
- Voice assistants
- 3D AI avatars
- Research / training

---

**You now have a FULL production‑grade AI API 🚀**

