$ uvicorn api.app:app --reload

INFO:     Waiting for application startup.
2025-12-12 01:20:40,903 - API - INFO - 🚀 AI Friend API starting...
2025-12-12 01:20:40,905 - API - INFO - ✅ Redis rate limiter initialized
2025-12-12 01:20:40,905 - API - INFO - ✅ AI Friend API ready!
INFO:     Application startup complete.
INFO:     127.0.0.1:42346 - "GET /doc HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:42346 - "GET /favicon.ico HTTP/1.1" 404 Not Found
2025-12-12 01:21:01,399 - Middleware - ERROR - Unhandled error: module 'datetime' has no attribute 'now'
INFO:     127.0.0.1:42350 - "GET /health HTTP/1.1" 500 Internal Server Error
^CINFO:     Shutting down
INFO:     Waiting for application shutdown.
2025-12-12 01:21:37,023 - API - INFO - 👋 AI Friend API shutting down...
INFO:     Application shutdown complete.
INFO:     Finished server process [33794]
INFO:     Stopping reloader process [33791]
(venv) ashish@ashish-Latitude-7320:~/Documents/fbot3/ai_friend_system$ redis-server
34212:C 12 Dec 2025 01:22:10.088 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
34212:C 12 Dec 2025 01:22:10.088 # Redis version=6.0.16, bits=64, commit=00000000, modified=0, pid=34212, just started
34212:C 12 Dec 2025 01:22:10.088 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
34212:M 12 Dec 2025 01:22:10.089 # Could not create server TCP listening socket *:6379: bind: Address already in use
(venv) ashish@ashish-Latitude-7320:~/Documents/fbot3/ai_friend_system$ uvicorn api.app:app --reload
INFO:     Will watch for changes in these directories: ['/home/ashish/Documents/fbot3/ai_friend_system']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [34275] using WatchFiles
INFO:     Started server process [34277]
INFO:     Waiting for application startup.
2025-12-12 01:22:27,956 - API - INFO - 🚀 AI Friend API starting...
2025-12-12 01:22:27,958 - API - INFO - ✅ Redis rate limiter initialized
2025-12-12 01:22:27,958 - API - INFO - ✅ AI Friend API ready!

🚀 AI FRIEND - COMPLETE API REFERENCE DOCUMENTATION
📋 BASE URL
Development:  http://localhost:8000
Production:   https://your-domain.com
🔐 AUTHENTICATION
All protected endpoints require JWT token in header:
httpAuthorization: Bearer <your_jwt_token>

📑 TABLE OF CONTENTS

Authentication APIs (3 endpoints)
Chat APIs (5 endpoints)
Memory APIs (5 endpoints)
Voice APIs (4 endpoints)
Profile APIs (3 endpoints)
Analytics APIs (3 endpoints)
Persona APIs (3 endpoints)
Avatar APIs (3 endpoints)
Agent APIs (2 endpoints)
System APIs (3 endpoints)

TOTAL: 34 API ENDPOINTS

🔐 AUTHENTICATION APIs
1. Register User
httpPOST /api/auth/register
Description: Create a new user account
Authentication: None (Public)
Request Body:
json{
  "username": "john_doe",
  "password": "SecurePass123!",
  "email": "john@example.com",
  "name": "John Doe"
}
Response (201 Created):
json{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
Timing: ~50ms (includes password hashing)
Error Responses:
json// 400 - Username already exists
{
  "detail": "Username already exists"
}

// 422 - Validation error
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error"
    }
  ]
}

2. Login User
httpPOST /api/auth/login
Description: Authenticate and get JWT token
Authentication: None (Public)
Request Body:
json{
  "username": "john_doe",
  "password": "SecurePass123!"
}
Response (200 OK):
json{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
Timing: ~30ms (includes password verification)
Error Responses:
json// 401 - Invalid credentials
{
  "detail": "Invalid credentials"
}

3. Logout User
httpPOST /api/auth/logout
Description: Invalidate current token (blacklist it)
Authentication: Required
Headers:
httpAuthorization: Bearer <token>
Response (200 OK):
json{
  "message": "Logged out successfully"
}
Timing: ~10ms

💬 CHAT APIs
1. Send Message (Standard)
httpPOST /api/chat/send
Description: Send message and get AI response
Authentication: Required
Request Body:
json{
  "message": "I'm feeling great today!",
  "context": {
    "location": "home",
    "time_of_day": "morning"
  },
  "save_to_memory": true
}
Response (200 OK):
json{
  "response": "That's wonderful to hear! I can tell you're in a great mood today. What's made you feel so good?",
  "emotion": {
    "primary_emotion": "joy",
    "confidence": 0.85,
    "all_emotions": {
      "joy": 0.85,
      "excitement": 0.3
    },
    "sentiment_score": 0.8,
    "subjectivity": 0.6,
    "intensity": "high"
  },
  "processing_time": 0.387,
  "memories_used": 3,
  "session_id": "abc-123-def-456"
}
Timing:

First request: ~390ms (no cache)
Cached request: ~10ms
Optimized: ~155ms (with GPU)

Rate Limit: 60 requests/minute per user

2. Stream Chat Response (SSE)
httpGET /api/chat/stream?message={text}
Description: Stream AI response word-by-word (like ChatGPT)
Authentication: Required
Query Parameters:

message (required): User's message

Response (text/event-stream):
event: message
data: That's

event: message
data: wonderful

event: message
data: to

event: message
data: hear!

event: done
data: complete
JavaScript Client Example:
javascriptconst eventSource = new EventSource(
  '/api/chat/stream?message=Hello'
);

eventSource.onmessage = (event) => {
  if (event.data === 'complete') {
    eventSource.close();
  } else {
    console.log('Token:', event.data);
  }
};
Timing:

First token: ~150ms
Subsequent tokens: ~20ms each
Total perceived delay: ~200ms (feels faster!)


3. WebSocket Chat
httpWS /api/chat/ws/{user_id}
Description: Real-time bidirectional chat
Authentication: Via query parameter ?token=<jwt_token>
WebSocket Messages:
Send (Client → Server):
json{
  "message": "Hello AI!",
  "timestamp": "2025-12-06T10:30:00Z"
}
Receive (Server → Client):
json{
  "response": "Hello! How are you?",
  "emotion": {
    "primary_emotion": "friendly",
    "confidence": 0.9
  },
  "processing_time": 0.245,
  "timestamp": "2025-12-06T10:30:00.245Z"
}
JavaScript Client Example:
javascriptconst ws = new WebSocket(
  'ws://localhost:8000/api/chat/ws/john_doe?token=<jwt>'
);

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "Hello!",
    timestamp: new Date().toISOString()
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('AI:', data.response);
};
Timing: ~200ms per message

4. Get Chat History
httpGET /api/chat/history?limit={num}
Description: Retrieve conversation history
Authentication: Required
Query Parameters:

limit (optional, default: 50): Number of messages

Response (200 OK):
json{
  "conversation_id": 123,
  "session_id": "abc-123",
  "user_id": "john_doe",
  "stats": {
    "message_count": 150,
    "avg_processing_time": 0.312
  },
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Hello!",
      "emotion": "neutral",
      "timestamp": "2025-12-06T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Hi! How are you?",
      "emotion": "friendly",
      "timestamp": "2025-12-06T10:00:00.245Z"
    }
  ]
}
Timing: ~15ms (from cache), ~50ms (from DB)

5. Clear Conversation
httpDELETE /api/chat/clear
Description: Clear current conversation and start fresh
Authentication: Required
Response (200 OK):
json{
  "message": "Conversation cleared",
  "new_session_id": "def-456-ghi-789"
}
Timing: ~20ms

🧠 MEMORY APIs
1. Save Memory
httpPOST /api/memory/save
Description: Manually save important memory
Authentication: Required
Request Body:
json{
  "content": "User's birthday is June 15th",
  "category": "personal_info",
  "importance": 0.95,
  "tags": ["birthday", "personal", "important"]
}
Response (200 OK):
json{
  "memory_id": "mem-123-abc",
  "message": "Memory saved",
  "tier": "permanent",
  "expires_at": null
}
Timing: ~30ms (sync), ~5ms (async background save)

2. Search Memories
httpPOST /api/memory/search
Description: Semantic search through memories
Authentication: Required
Request Body:
json{
  "query": "What did I say about my job?",
  "limit": 10,
  "category": "work"
}
Response (200 OK):
json{
  "memories": [
    {
      "id": "mem-456",
      "content": "I love my job as a developer",
      "metadata": {
        "category": "work",
        "importance": 0.8,
        "tags": ["job", "developer"],
        "timestamp": "2025-12-01T10:00:00Z"
      },
      "distance": 0.06,
      "similarity": 0.94
    },
    {
      "id": "mem-789",
      "content": "Working on AI project at work",
      "metadata": {
        "category": "work",
        "importance": 0.75,
        "tags": ["work", "project"],
        "timestamp": "2025-12-03T14:30:00Z"
      },
      "distance": 0.13,
      "similarity": 0.87
    }
  ],
  "count": 2,
  "search_time_ms": 45
}
Timing:

Without cache: ~60ms
With cache: ~10ms
With optimized index: ~25ms


3. Delete Memory
httpDELETE /api/memory/{memory_id}
Description: Delete specific memory
Authentication: Required
Path Parameters:

memory_id (required): Memory ID to delete

Response (200 OK):
json{
  "message": "Memory deleted",
  "memory_id": "mem-123"
}
Timing: ~15ms

4. Get Memory Stats
httpGET /api/memory/stats
Description: Get memory usage statistics
Authentication: Required
Response (200 OK):
json{
  "total_memories": 324,
  "by_tier": {
    "session": 45,
    "sub_temporary": 89,
    "temporary": 120,
    "permanent": 58,
    "personal": 12
  },
  "by_category": {
    "work": 78,
    "personal": 45,
    "hobbies": 34,
    "relationships": 23
  },
  "total_size_mb": 2.4,
  "oldest_memory": "2025-01-15T10:00:00Z",
  "newest_memory": "2025-12-06T10:00:00Z"
}
Timing: ~20ms

5. Get Memory Tiers Info
httpGET /api/memory/tiers
Description: Get information about memory tier system
Authentication: None (Public)
Response (200 OK):
json{
  "tiers": [
    {
      "name": "session",
      "retention_days": 2,
      "description": "Recent conversation context",
      "auto_cleanup": true
    },
    {
      "name": "sub_temporary",
      "retention_days": 10,
      "description": "Recent important information",
      "auto_cleanup": true
    },
    {
      "name": "temporary",
      "retention_days": 30,
      "description": "Medium-term memories",
      "auto_cleanup": true
    },
    {
      "name": "permanent",
      "retention_days": -1,
      "description": "Very important, never deleted",
      "auto_cleanup": false
    },
    {
      "name": "personal",
      "retention_days": -1,
      "description": "Personal information, encrypted",
      "auto_cleanup": false
    }
  ]
}
Timing: ~2ms

🎤 VOICE APIs
1. Speech to Text
httpPOST /api/voice/stt
Description: Convert audio to text
Authentication: Required
Request (multipart/form-data):
Content-Type: multipart/form-data

audio: <audio_file.wav>
language: en-US (optional)
Response (200 OK):
json{
  "text": "Hello, how are you today?",
  "confidence": 0.95,
  "language": "en-US",
  "duration_seconds": 2.3,
  "processing_time_ms": 1800
}
Timing: ~2000ms (depends on audio length)
Supported Formats: WAV, MP3, OGG, FLAC

2. Text to Speech
httpPOST /api/voice/tts
Description: Convert text to speech audio
Authentication: Required
Request Body:
json{
  "text": "Hello! How are you today?",
  "voice_id": "default",
  "speed": 1.0,
  "pitch": 1.0,
  "emotion": "friendly"
}
Response (200 OK):
json{
  "audio_url": "/audio/output_abc123.mp3",
  "duration_seconds": 3.5,
  "size_bytes": 56000,
  "format": "mp3",
  "sample_rate": 22050
}
Timing: ~500ms (for 10 words)

3. Voice Stream (WebSocket)
httpWS /api/voice/stream/{user_id}
Description: Real-time voice chat with streaming
Authentication: Via query parameter
Send (Binary Audio Chunks):
Binary data: PCM audio @ 16kHz
Receive (JSON):
json{
  "type": "transcription",
  "text": "Hello",
  "is_final": false
}

{
  "type": "response",
  "text": "Hi! How are you?",
  "audio_chunk": "<base64_audio_data>"
}
Timing:

Transcription latency: ~500ms
Response latency: ~200ms
Audio playback: Real-time


4. Get Audio Devices
httpGET /api/voice/devices
Description: List available microphones
Authentication: Required
Response (200 OK):
json{
  "devices": [
    {
      "index": 0,
      "name": "Built-in Microphone",
      "channels": 2,
      "sample_rate": 44100,
      "is_default": true
    },
    {
      "index": 1,
      "name": "USB Microphone",
      "channels": 1,
      "sample_rate": 48000,
      "is_default": false
    }
  ],
  "default_device": 0
}
Timing: ~5ms

👤 PROFILE APIs
1. Get User Profile
httpGET /api/profile/{user_id}
Description: Get user profile information
Authentication: Required (own profile or admin)
Response (200 OK):
json{
  "user_id": "john_doe",
  "name": "John Doe",
  "email": "john@example.com",
  "preferences": {
    "tone": "friendly",
    "formality": "casual",
    "language": "en-US"
  },
  "personality_traits": {
    "curious": true,
    "empathetic": true,
    "humorous": false
  },
  "interests": ["AI", "technology", "music", "books"],
  "created_at": "2025-01-01T10:00:00Z",
  "last_active": "2025-12-06T10:00:00Z",
  "total_conversations": 45,
  "total_messages": 1247
}
Timing: ~15ms

2. Update User Profile
httpPUT /api/profile/{user_id}
Description: Update profile information
Authentication: Required (own profile only)
Request Body:
json{
  "name": "John Smith",
  "preferences": {
    "tone": "professional",
    "formality": "formal"
  },
  "interests": ["AI", "machine learning", "robotics"]
}
Response (200 OK):
json{
  "message": "Profile updated successfully",
  "user_id": "john_doe",
  "updated_fields": ["name", "preferences", "interests"]
}
Timing: ~25ms

3. Delete User Profile
httpDELETE /api/profile/{user_id}
Description: Delete user account and all data
Authentication: Required (own profile only)
Response (200 OK):
json{
  "message": "Profile deleted successfully",
  "user_id": "john_doe",
  "deleted_data": {
    "conversations": 45,
    "messages": 1247,
    "memories": 324
  }
}
Timing: ~100ms (background cleanup continues)

📊 ANALYTICS APIs
1. Get Analytics Overview
httpGET /api/analytics/overview
Description: Get comprehensive analytics dashboard
Authentication: Required
Query Parameters:

period (optional): "day", "week", "month", "all" (default: "week")

Response (200 OK):
json{
  "period": "week",
  "total_interactions": 150,
  "avg_session_length_minutes": 15.5,
  "most_active_time": "18:00-20:00",
  "emotion_distribution": {
    "joy": 45,
    "neutral": 30,
    "sad": 15,
    "excited": 10
  },
  "top_topics": [
    {"topic": "work", "count": 35, "sentiment": 0.6},
    {"topic": "hobbies", "count": 28, "sentiment": 0.8},
    {"topic": "relationships", "count": 20, "sentiment": 0.5}
  ],
  "memory_stats": {
    "total_memories": 324,
    "important_memories": 89,
    "recent_memories": 45
  },
  "performance": {
    "avg_response_time_ms": 387,
    "fastest_response_ms": 125,
    "slowest_response_ms": 1200
  }
}
Timing: ~50ms (cached), ~150ms (computed)

2. Get Emotion Trends
httpGET /api/analytics/emotion-trends?days={num}
Description: Get emotion trends over time
Authentication: Required
Query Parameters:

days (optional, default: 7): Number of days to analyze

Response (200 OK):
json{
  "period": "last_7_days",
  "trends": [
    {
      "date": "2025-12-01",
      "emotions": {
        "joy": 0.7,
        "sadness": 0.1,
        "neutral": 0.2
      },
      "avg_sentiment": 0.65,
      "message_count": 25
    },
    {
      "date": "2025-12-02",
      "emotions": {
        "joy": 0.8,
        "sadness": 0.05,
        "neutral": 0.15
      },
      "avg_sentiment": 0.75,
      "message_count": 30
    }
  ],
  "overall_trend": "improving",
  "happiness_score": 7.5
}
Timing: ~80ms

3. Get Topic Analysis
httpGET /api/analytics/topics
Description: Analyze conversation topics
Authentication: Required
Response (200 OK):
json{
  "topics": [
    {
      "name": "Career",
      "frequency": 45,
      "percentage": 30.0,
      "sentiment": 0.6,
      "keywords": ["work", "job", "project", "meeting", "deadline"],
      "trend": "increasing",
      "last_discussed": "2025-12-06T09:00:00Z"
    },
    {
      "name": "Health",
      "frequency": 30,
      "percentage": 20.0,
      "sentiment": 0.5,
      "keywords": ["exercise", "sleep", "stress", "health"],
      "trend": "stable",
      "last_discussed": "2025-12-05T18:00:00Z"
    }
  ],
  "total_topics": 8,
  "most_discussed": "Career",
  "most_positive": "Hobbies",
  "needs_attention": ["Stress", "Sleep"]
}
Timing: ~100ms

🎭 PERSONA APIs
1. Get Persona Configuration
httpGET /api/persona/get
Description: Get current AI persona settings
Authentication: Required
Response (200 OK):
json{
  "name": "Friend",
  "personality_traits": {
    "friendliness": 0.9,
    "humor": 0.7,
    "empathy": 0.9,
    "formality": 0.3,
    "enthusiasm": 0.8
  },
  "speaking_style": "casual",
  "interests": ["technology", "music", "books", "philosophy"],
  "background_story": "I'm an AI companion designed to be your thoughtful friend...",
  "voice_id": "friendly_female_01",
  "language": "en-US"
}
Timing: ~5ms

2. Update Persona
httpPOST /api/persona/update
Description: Customize AI personality
Authentication: Required
Request Body:
json{
  "name": "Sage",
  "personality_traits": {
    "friendliness": 0.8,
    "humor": 0.5,
    "empathy": 0.95,
    "formality": 0.6
  },
  "speaking_style": "thoughtful",
  "interests": ["philosophy", "psychology", "science"],
  "background_story": "I'm a wise and thoughtful AI companion..."
}
Response (200 OK):
json{
  "message": "Persona updated successfully",
  "config": { /* updated config */ },
  "changes_applied": true,
  "restart_required": false
}
Timing: ~15ms

3. Reset Persona
httpPOST /api/persona/reset
Description: Reset to default persona
Authentication: Required
Response (200 OK):
json{
  "message": "Persona reset to default",
  "config": { /* default config */ }
}
Timing: ~10ms

🎨 AVATAR APIs
1. Set Expression
httpPOST /api/avatar/expression
Description: Control 3D avatar facial expression
Authentication: Required
Request Body:
json{
  "emotion": "happy",
  "intensity": 0.8,
  "duration": 2.0,
  "transition_speed": "fast"
}
Response (200 OK):
json{
  "emotion": "happy",
  "expression_params": {
    "smile": 0.9,
    "eyebrows": 0.2,
    "eyes_open": 0.8,
    "mouth_open": 0.1
  },
  "intensity": 0.8,
  "duration": 2.0,
  "blend_shapes": {
    "jawOpen": 0.1,
    "mouthSmile": 0.9,
    "browInnerUp": 0.2
  }
}
Timing: ~3ms

2. Play Animation
httpPOST /api/avatar/animation
Description: Trigger avatar animation
Authentication: Required
Request Body:
json{
  "animation_type": "talking",
  "loop": true,
  "speed": 1.0
}
Response (200 OK):
json{
  "animation": "talking",
  "params": {
    "mouth_movement": true,
    "head_bob": 0.1,
    "blink_rate": 0.2
  },
  "duration": 1.0,
  "loop": true,
  "animation_id": "anim-123"
}
Timing: ~2ms

3. Get Lip Sync Data
httpGET /api/avatar/sync-speech?text={text}
Description: Get phoneme timing for lip-sync
Authentication: Required
Query Parameters:

text (required): Text to be spoken

Response (200 OK):
json{
  "text": "Hello world",
  "duration": 1.2,
  "phonemes": [
    {"phoneme": "HH", "start": 0.0, "end": 0.1, "intensity": 0.8},
    {"phoneme": "EH", "start": 0.1, "end": 0.3, "intensity": 0.9},
    {"phoneme": "L", "start": 0.3, "end": 0.5, "intensity": 0.7},
    {"phoneme": "OW", "start": 0.5, "end": 0.8, "intensity": 0.9},
    {"phoneme": "W", "start": 0.9, "end": 1.0, "intensity": 0.6},
    {"phoneme": "ER", "start": 1.0, "end": 1.1, "intensity": 0.7},
    {"phoneme": "D", "start": 1.1, "end": 1.2, "intensity": 0.5}
  ],
  "visemes": ["A", "E", "I", "O", "U"],
  "sample_rate": 100
}
Timing: ~50ms

🤖 AGENT APIs
1. Get Agent Status
httpGET /api/agents/status
Description: Get status of all agents
Authentication: Required
Response (200 OK):
json{
  "agents": [
    {
      "type": "emotion",
      "status": "active",
      "last_execution": "2025-12-06T10:30:15Z",
      "avg_execution_time_ms": 25,
      "total_executions": 1247,
      "success_rate": 0.998
    },
    {
      "type": "context",
      "status": "active",
      "last_execution": "2025-12-06T10:30:15Z",
      "avg_execution_time_ms": 40,
      "total_executions": 1247,
      "success_rate": 0.995
    },
    {
      "type": "task",
      "status": "active",
      "last_execution": "2025-12-06T10:30:15Z",
      "avg_execution_time_ms": 30,
      "total_executions": 1247,
      "success_rate": 0.997
    }
  ],
  "coordinator": {
    "parallel_execution": true,
    "avg_total_time_ms": 42,
    "speedup_factor": 2.38
  }
}
Timing: ~5ms

2. Test Agent
httpPOST /api/agents/test
Description: Test specific agent with sample input
Authentication: Required
Request Body:
json{
  "agent_type": "emotion",
  "input": "I'm so excited about this project!"
}
Response (200 OK):
json{
  "agent_type": "emotion",
  "input": "I'm so excited about this project!",
  "output": {
    "primary_emotion": "excitement",
    "confidence": 0.92,
    "sentiment_score": 0.85,
    "intensity": "high"
  },
  "execution_time_ms": 28,
  "success": true
}
Timing: Varies by agent (25-50ms)

⚙️ SYSTEM APIs
1. Health Check
httpGET /health
Description: Check if API is running
Authentication: None (Public)
Response (200 OK):
json{
  "status": "healthy",
  "timestamp": "2025-12-06T10:30:00Z",
  "version": "2.0.0",
  "uptime_seconds": 86400
}
Timing: ~1ms

2. System Stats
httpGET /stats
Description: Get system statistics
Authentication: Required (Admin only)
Response (200 OK):
json{
  "active_sessions": 15,
  "session_info": [
    {
      "user_id": "john_doe",
      "created_at": "2025-12-06T09:00:00Z",
      "last_accessed": "2025-12-06T10:29:00Z"
    }
  ],
  "total_users": 245,
  "total_conversations": 1523,
  "total_messages": 45678,
  "database_size_mb": 234.5,
  "memory_usage_mb": 512.3,
  "cpu_usage_percent": 23.5,
  "requests_per_minute": 45
}
Timing: ~20ms

3. API Documentation
httpGET /docs
Description: Interactive API documentation (Swagger UI)
Authentication: None (Public)
Response: HTML page with interactive API explorer
Timing: ~10ms
