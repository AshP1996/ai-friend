# Complete API Documentation

## Table of Contents
1. [Base Information](#base-information)
2. [Authentication APIs](#authentication-apis)
3. [Chat APIs](#chat-apis)
4. [Voice APIs](#voice-apis)
5. [Memory APIs](#memory-apis)
6. [Persona APIs](#persona-apis)
7. [Profile APIs](#profile-apis)
8. [Avatar APIs](#avatar-apis)
9. [Analytics APIs](#analytics-apis)
10. [Agents APIs](#agents-apis)
11. [Error Handling](#error-handling)

---

## Base Information

### Base URL
```
http://localhost:8000
```

### API Prefix
```
/api
```

### Authentication
Currently using anonymous user IDs. Each request generates a temporary `user_id` automatically.

**Note**: For production, use JWT authentication via `/api/auth/login` endpoint.

### Response Format
All responses are JSON unless specified otherwise.

### WebSocket Protocol
WebSocket endpoints use JSON for text messages and binary for audio data.

---

## Authentication APIs

### 1. Register User

**Endpoint**: `POST /api/auth/register`

**Description**: Register a new user account

**Request Body**:
```json
{
  "username": "string (required, min: 3, max: 50)",
  "password": "string (required, min: 6, max: 64)",
  "email": "string (optional)",
  "name": "string (optional)"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400 Bad Request`: Username already exists
```json
{
  "detail": "Username already exists"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123",
    "email": "john@example.com",
    "name": "John Doe"
  }'
```

---

### 2. Login

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticate user and get access token

**Request Body**:
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
```json
{
  "detail": "Invalid credentials"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'
```

---

### 3. Logout

**Endpoint**: `POST /api/auth/logout`

**Description**: Logout user (invalidates token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## Chat APIs

### 1. Send Message

**Endpoint**: `POST /api/chat/send`

**Description**: Send a message to AI friend with full processing (emotion analysis, memory retrieval, response generation)

**Request Body**:
```json
{
  "message": "string (required) - User's message",
  "context": {
    "optional": "additional context data"
  },
  "save_to_memory": true
}
```

**Response** (200 OK):
```json
{
  "response": "I'm doing great! How about you?",
  "emotion": {
    "primary_emotion": "happy",
    "confidence": 0.85,
    "all_emotions": {
      "joy": 0.85,
      "neutral": 0.15
    },
    "sentiment_score": 0.7,
    "subjectivity": 0.6,
    "intensity": "medium"
  },
  "processing_time": 1.234,
  "memories_used": 3,
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:
- `500 Internal Server Error`
```json
{
  "detail": "Error message"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/chat/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How are you today?",
    "save_to_memory": true
  }'
```

**Performance**: ~1.5-3 seconds (optimized with caching)

---

### 2. Stream Chat Response

**Endpoint**: `GET /api/chat/stream`

**Description**: Get streaming chat response (Server-Sent Events)

**Query Parameters**:
- `message` (string, required): User's message
- `user_id` (string, auto-generated): User identifier

**Response** (200 OK, text/event-stream):
```
event: message
data: Hello

event: message
data: there!

event: message
data: How

event: message
data: can

event: message
data: I

event: message
data: help?

event: done
data: complete
```

**Example** (JavaScript):
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/chat/stream?message=Hello'
);

eventSource.addEventListener('message', (e) => {
  console.log('Word:', e.data);
});

eventSource.addEventListener('done', () => {
  eventSource.close();
});
```

---

### 3. WebSocket Chat

**Endpoint**: `WS /api/chat/ws/{user_id}`

**Description**: Real-time bidirectional chat via WebSocket

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws/user123');
```

**Send Message** (Text):
```json
"Hello, how are you?"
```

**Receive Response** (JSON):
```json
{
  "response": "I'm doing great! Thanks for asking!",
  "emotion": {
    "emotion": "happy",
    "confidence": 0.8
  },
  "processing_time": 1.5
}
```

**Example**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws/user123');

ws.onopen = () => {
  ws.send("Hello!");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Response:', data.response);
  console.log('Emotion:', data.emotion);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

### 4. Get Chat History

**Endpoint**: `GET /api/chat/history`

**Description**: Get conversation history and statistics

**Query Parameters**:
- `user_id` (string, auto-generated): User identifier
- `limit` (int, optional, default: 50): Number of messages to retrieve

**Response** (200 OK):
```json
{
  "conversation_id": 123,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "stats": {
    "message_count": 45,
    "avg_processing_time": 1.2,
    "total_duration": 3600
  }
}
```

**Example**:
```bash
curl "http://localhost:8000/api/chat/history?limit=50"
```

---

### 5. Clear Conversation

**Endpoint**: `DELETE /api/chat/clear`

**Description**: Clear conversation history and cache for user

**Response** (200 OK):
```json
{
  "message": "Conversation cleared"
}
```

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/chat/clear"
```

---

### 6. Get Performance Stats

**Endpoint**: `GET /api/chat/performance`

**Description**: Get system performance statistics

**Response** (200 OK):
```json
{
  "performance": {
    "total_requests": 1250,
    "avg_response_time": 1.45,
    "p95_response_time": 2.8,
    "p99_response_time": 4.2,
    "min_response_time": 0.3,
    "max_response_time": 5.1,
    "cache_hits": 450,
    "cache_misses": 800,
    "agent_timeouts": 5,
    "llm_timeouts": 2
  },
  "cache": {
    "hits": 450,
    "misses": 800,
    "hit_rate": 36.0
  }
}
```

---

## Voice APIs

### 1. Voice Stream (WebSocket)

**Endpoint**: `WS /api/voice/stream/{user_id}`

**Description**: Real-time voice chat with emotion detection and pitch analysis

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/voice/stream/user123');
```

**Send**: Binary PCM audio data (16-bit, 16kHz, mono, WAV format)

**Receive Messages** (JSON):

**Status Update**:
```json
{
  "type": "status",
  "state": "listening|thinking|speaking",
  "emotion": "happy"
}
```

**Partial Transcription**:
```json
{
  "type": "partial",
  "text": "Hello how are..."
}
```

**Final Response**:
```json
{
  "type": "response",
  "text": "I'm doing great! How about you?",
  "emotion": "happy"
}
```

**Receive Audio**: Binary WAV data (chunked, 4KB chunks)

**Example** (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/api/voice/stream/user123');
const audioContext = new AudioContext();

ws.onopen = () => {
  // Start recording audio
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          // Convert to PCM and send
          convertToPCM(event.data).then(pcm => {
            ws.send(pcm);
          });
        }
      };
      
      mediaRecorder.start(100); // Send every 100ms
    });
};

ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // Audio chunk received
    playAudio(event.data);
  } else {
    const msg = JSON.parse(event.data);
    
    switch(msg.type) {
      case 'status':
        updateAvatarState(msg.state, msg.emotion);
        break;
      case 'partial':
        updateTranscription(msg.text);
        break;
      case 'response':
        displayResponse(msg.text, msg.emotion);
        break;
    }
  }
};
```

**Features**:
- Real-time pitch detection
- Emotion analysis from voice + text
- Emotion-aware voice synthesis
- Chunked audio streaming (low latency)
- Natural human-like speech patterns

---

## Memory APIs

### 1. Save Memory

**Endpoint**: `POST /api/memory/save`

**Description**: Save important information to semantic memory

**Request Body**:
```json
{
  "content": "string (required) - Memory content",
  "category": "string (optional, default: 'general')",
  "importance": 0.5,
  "tags": ["tag1", "tag2"]
}
```

**Response** (200 OK):
```json
{
  "memory_id": "mem_abc123",
  "message": "Memory saved"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/memory/save" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User loves playing guitar",
    "category": "hobbies",
    "importance": 0.8,
    "tags": ["music", "guitar", "hobby"]
  }'
```

---

### 2. Search Memories

**Endpoint**: `POST /api/memory/search`

**Description**: Semantic search through stored memories

**Request Body**:
```json
{
  "query": "string (required) - Search query",
  "limit": 10,
  "category": "string (optional)"
}
```

**Response** (200 OK):
```json
{
  "memories": [
    {
      "id": "mem_abc123",
      "content": "User loves playing guitar",
      "metadata": {
        "category": "hobbies",
        "importance": 0.8,
        "tags": ["music", "guitar"],
        "timestamp": "2025-12-01T10:30:00Z"
      },
      "similarity": 0.92
    }
  ],
  "count": 1
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the user like?",
    "limit": 5
  }'
```

---

### 3. Delete Memory

**Endpoint**: `DELETE /api/memory/{memory_id}`

**Description**: Delete a specific memory

**Path Parameters**:
- `memory_id` (string, required): Memory identifier

**Response** (200 OK):
```json
{
  "message": "Memory deleted"
}
```

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/memory/mem_abc123"
```

---

### 4. Get Memory Statistics

**Endpoint**: `GET /api/memory/stats`

**Description**: Get memory statistics for user

**Response** (200 OK):
```json
{
  "total_memories": 89,
  "user_id": "user123"
}
```

---

## Persona APIs

### 1. Get Persona

**Endpoint**: `GET /api/persona/get`

**Description**: Get current persona configuration

**Response** (200 OK):
```json
{
  "name": "Friend",
  "personality_traits": {
    "friendliness": 0.9,
    "humor": 0.7,
    "empathy": 0.9,
    "formality": 0.3
  },
  "speaking_style": "casual",
  "interests": ["technology", "music", "books"],
  "background_story": null,
  "voice_id": null
}
```

**Example**:
```bash
curl "http://localhost:8000/api/persona/get"
```

---

### 2. Update Persona

**Endpoint**: `POST /api/persona/update`

**Description**: Update persona configuration

**Request Body**:
```json
{
  "name": "Alex",
  "personality_traits": {
    "friendliness": 0.95,
    "humor": 0.8,
    "empathy": 0.9,
    "formality": 0.2
  },
  "speaking_style": "casual",
  "interests": ["AI", "technology", "gaming", "movies"],
  "background_story": "A friendly AI companion who loves technology",
  "voice_id": "voice_001"
}
```

**Response** (200 OK):
```json
{
  "message": "Persona updated",
  "config": {
    "name": "Alex",
    "personality_traits": {...},
    "speaking_style": "casual",
    "interests": [...],
    "background_story": "...",
    "voice_id": "voice_001"
  }
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/persona/update" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex",
    "personality_traits": {
      "friendliness": 0.95,
      "humor": 0.8
    },
    "speaking_style": "casual",
    "interests": ["AI", "technology"]
  }'
```

---

### 3. Reset Persona

**Endpoint**: `POST /api/persona/reset`

**Description**: Reset persona to default configuration

**Response** (200 OK):
```json
{
  "message": "Persona reset to default",
  "config": {
    "name": "Friend",
    "personality_traits": {
      "friendliness": 0.9,
      "humor": 0.7,
      "empathy": 0.9,
      "formality": 0.3
    },
    "speaking_style": "casual",
    "interests": ["technology", "music", "books"],
    "background_story": null,
    "voice_id": null
  }
}
```

---

## Profile APIs

### 1. Get Profile

**Endpoint**: `GET /api/profile/{user_id}`

**Description**: Get user profile information

**Path Parameters**:
- `user_id` (string, required): User identifier

**Response** (200 OK):
```json
{
  "user_id": "user123",
  "profile": {}
}
```

---

### 2. Update Profile

**Endpoint**: `PUT /api/profile/{user_id}`

**Description**: Update user profile

**Path Parameters**:
- `user_id` (string, required): User identifier

**Request Body**:
```json
{
  "name": "string (optional)",
  "preferences": "string (optional)",
  "interests": "string (optional)"
}
```

**Response** (200 OK):
```json
{
  "message": "Profile updated",
  "user_id": "user123"
}
```

---

## Avatar APIs

### 1. Set Expression

**Endpoint**: `POST /api/avatar/expression`

**Description**: Set avatar facial expression based on emotion

**Request Body**:
```json
{
  "emotion": "happy|sad|excited|neutral|angry|surprised",
  "intensity": 0.8,
  "duration": 2.0
}
```

**Response** (200 OK):
```json
{
  "emotion": "happy",
  "expression_params": {
    "smile": 0.9,
    "eyebrows": 0.2
  },
  "intensity": 0.8,
  "duration": 2.0
}
```

**Expression Parameters**:
- `smile`: -1.0 (sad) to 1.0 (happy)
- `eyebrows`: -1.0 (angry) to 1.0 (surprised)
- `eyes`: 0.0 (closed) to 1.0 (wide open)
- `mouth`: 0.0 (closed) to 1.0 (open)

**Example**:
```bash
curl -X POST "http://localhost:8000/api/avatar/expression" \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "happy",
    "intensity": 0.9,
    "duration": 3.0
  }'
```

---

### 2. Play Animation

**Endpoint**: `POST /api/avatar/animation`

**Description**: Trigger avatar animation

**Request Body**:
```json
{
  "animation_type": "talking|listening|thinking|idle",
  "loop": false
}
```

**Response** (200 OK):
```json
{
  "animation": "talking",
  "params": {
    "mouth_movement": true,
    "duration": 1.0
  },
  "loop": false
}
```

**Animation Types**:
- `talking`: Mouth movement synchronized with speech
- `listening`: Head tilt, eye focus on user
- `thinking`: Hand to chin, looking up
- `idle`: Breathing, blinking, subtle movements

**Example**:
```bash
curl -X POST "http://localhost:8000/api/avatar/animation" \
  -H "Content-Type: application/json" \
  -d '{
    "animation_type": "talking",
    "loop": true
  }'
```

---

### 3. Get Lip-Sync Data

**Endpoint**: `GET /api/avatar/sync-speech`

**Description**: Get phoneme timing for lip-sync animation

**Query Parameters**:
- `text` (string, required): Text to analyze
- `user_id` (string, auto-generated): User identifier

**Response** (200 OK):
```json
{
  "text": "Hello there",
  "duration": 0.55,
  "phonemes": [
    {
      "phoneme": "HH",
      "start": 0.0,
      "end": 0.05
    },
    {
      "phoneme": "EH",
      "start": 0.05,
      "end": 0.15
    },
    {
      "phoneme": "L",
      "start": 0.15,
      "end": 0.25
    },
    {
      "phoneme": "OW",
      "start": 0.25,
      "end": 0.35
    },
    {
      "phoneme": "DH",
      "start": 0.35,
      "end": 0.4
    },
    {
      "phoneme": "EH",
      "start": 0.4,
      "end": 0.5
    },
    {
      "phoneme": "R",
      "start": 0.5,
      "end": 0.55
    }
  ]
}
```

**Example**:
```bash
curl "http://localhost:8000/api/avatar/sync-speech?text=Hello%20there"
```

---

## Analytics APIs

### 1. Get Analytics Overview

**Endpoint**: `GET /api/analytics/overview`

**Description**: Get comprehensive analytics dashboard data

**Response** (200 OK):
```json
{
  "total_interactions": 150,
  "avg_session_length": 15.5,
  "most_active_time": "18:00-20:00",
  "emotion_distribution": {
    "happy": 45,
    "neutral": 30,
    "sad": 15,
    "excited": 10
  },
  "top_topics": [
    {
      "topic": "work",
      "count": 35
    },
    {
      "topic": "hobbies",
      "count": 28
    },
    {
      "topic": "relationships",
      "count": 20
    }
  ],
  "memory_stats": {
    "total_memories": 89,
    "important_memories": 23,
    "recent_memories": 15
  }
}
```

---

### 2. Get Emotion Trends

**Endpoint**: `GET /api/analytics/emotion-trends`

**Description**: Get emotion trends over time

**Query Parameters**:
- `days` (int, optional, default: 7): Number of days to analyze
- `user_id` (string, auto-generated): User identifier

**Response** (200 OK):
```json
{
  "period": "last_7_days",
  "trends": [
    {
      "date": "2025-12-01",
      "happiness": 0.7,
      "sadness": 0.2,
      "excitement": 0.1
    },
    {
      "date": "2025-12-02",
      "happiness": 0.8,
      "sadness": 0.1,
      "excitement": 0.1
    }
  ]
}
```

---

### 3. Get Topic Analysis

**Endpoint**: `GET /api/analytics/topics`

**Description**: Analyze conversation topics

**Response** (200 OK):
```json
{
  "topics": [
    {
      "name": "Career",
      "frequency": 45,
      "sentiment": 0.6,
      "keywords": ["work", "job", "project", "meeting"]
    },
    {
      "name": "Health",
      "frequency": 30,
      "sentiment": 0.5,
      "keywords": ["exercise", "sleep", "stress"]
    }
  ]
}
```

---

## Agents APIs

### 1. Get Agents Status

**Endpoint**: `GET /api/agents/status`

**Description**: Get status of all AI agents

**Response** (200 OK):
```json
{
  "agents": [
    {
      "type": "emotion",
      "status": "active"
    },
    {
      "type": "context",
      "status": "active"
    },
    {
      "type": "task",
      "status": "active"
    }
  ]
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Error Scenarios

**Invalid Request Data**:
```json
{
  "detail": "Validation error: field 'message' is required"
}
```

**Authentication Error**:
```json
{
  "detail": "Invalid or expired token"
}
```

**Server Error**:
```json
{
  "detail": "Internal server error occurred"
}
```

---

## Rate Limiting

Currently, rate limiting is configured but may not be enforced in development mode.

**Production Limits**:
- 60 requests per minute per user
- 1000 requests per hour per user

---

## WebSocket Protocol

### Connection
```
ws://localhost:8000/api/chat/ws/{user_id}
ws://localhost:8000/api/voice/stream/{user_id}
```

### Message Types

**Text Messages**: JSON format
```json
{
  "type": "message_type",
  "data": {...}
}
```

**Binary Messages**: Audio data (PCM/WAV)

### Connection Lifecycle

1. **Connect**: Client establishes WebSocket connection
2. **Authenticate**: (Optional) Send authentication token
3. **Send/Receive**: Bidirectional communication
4. **Close**: Either party can close connection

### Error Handling

WebSocket errors are sent as JSON:
```json
{
  "type": "error",
  "message": "Error description"
}
```

---

## Best Practices

1. **Use WebSocket for Real-time**: Use WebSocket endpoints for real-time chat/voice
2. **Handle Errors Gracefully**: Always check for error responses
3. **Cache Responses**: Use cached responses when possible
4. **Batch Operations**: Combine multiple requests when possible
5. **Monitor Performance**: Check `/api/chat/performance` regularly

---

## Support

For issues or questions:
- Check logs: `data/logs/`
- Review performance stats: `GET /api/chat/performance`
- Check system health: `GET /health`

---

**Last Updated**: December 2025
**API Version**: 2.0.0
