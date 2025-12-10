# AI Friend System 🤖💬

A highly advanced, production-ready AI friend with voice capabilities, multi-tier memory management, and multi-agent processing.

## 🌟 Features

### Core Capabilities
- **🎙️ Voice Interaction**: Full speech-to-text and text-to-speech support
- **🧠 Multi-Tier Memory System**:
  - Session Memory (2 days)
  - Sub-Temporary Memory (10 days)
  - Temporary Memory (30 days)
  - Permanent Memory (forever)
  - Personal Info Storage (forever)
- **⚡ Lightning Fast Processing**: Parallel agent processing and threading
- **🤝 Multi-Agent System**:
  - Emotion Detection Agent
  - Context Understanding Agent
  - Task Recognition Agent
- **💾 Advanced Database**: SQLite with detailed schema and automatic cleanup
- **🔌 Flexible AI Models**: Support for Anthropic Claude and OpenAI GPT with automatic fallback

### Technical Features
- **Async/Await Architecture**: Non-blocking, high-performance operations
- **Parallel Processing**: Multiple agents run simultaneously
- **Memory Optimization**: Automatic memory consolidation and cleanup
- **RESTful API**: Full FastAPI implementation
- **Comprehensive Logging**: Detailed logging system
- **Error Handling**: Robust error handling and recovery
- **Modular Design**: Clean, maintainable architecture
- **Auto Database Creation**: Database is created automatically on first run

## 📋 Prerequisites

- Python 3.8+
- Microphone (for voice features)
- API Keys (at least one):
  - Anthropic API Key (recommended) - Get free tier at https://console.anthropic.com
  - OpenAI API Key (fallback)

## 🚀 Quick Start (3 Steps!)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**For voice support**, install PyAudio:
- **Windows**: `pip install pyaudio`
- **Mac**: `brew install portaudio && pip install pyaudio`
- **Linux**: `sudo apt-get install portaudio19-dev python3-pyaudio && pip install pyaudio`

### Step 2: Configure API Keys
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Get Free API Keys:**
- Anthropic Claude: https://console.anthropic.com (Free tier available!)
- OpenAI: https://platform.openai.com/api-keys

### Step 3: Run Setup (Optional but Recommended)
```bash
python setup_database.py
```

This will:
- ✅ Create the database
- ✅ Set up all tables and indexes
- ✅ Verify the structure
- ✅ Show database statistics

**OR** just run directly (database will auto-create):
```bash
python main.py --mode interactive
```

## 💻 Usage

### Interactive Mode (Recommended for First Use)

```bash
python main.py --mode interactive
```

Features in interactive mode:
- Type messages or use voice
- Switch between text/voice with commands
- View conversation summaries
- Real-time emotion detection
- Memory recall

Commands:
- `voice` - Switch to voice mode
- `text` - Switch to text mode
- `summary` - Show conversation stats
- `quit` - Exit

### API Server Mode

```bash
python main.py --mode api --host 0.0.0.0 --port 8000
```

Access:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## 🗃️ Database Management

### Manual Database Commands

```bash
# Create database
python -m database.init_db create

# Verify database structure
python -m database.init_db verify

# Show statistics
python -m database.init_db stats

# Create backup
python -m database.init_db backup

# Reset database (WARNING: deletes all data!)
python -m database.init_db reset
```

### Database Location
- Database file: `data/ai_friend.db`
- Backups: `data/backups/`
- Logs: `data/logs/`

### Database Schema

**Tables:**
1. **conversations** - Conversation sessions
2. **messages** - All chat messages
3. **memories** - Multi-tier memory storage
4. **user_profiles** - User information
5. **personal_info** - Personal data storage
6. **agent_logs** - Agent execution logs

**Indexes for Performance:**
- Message retrieval by conversation and time
- Memory search by tier and importance
- Expiration cleanup optimization

## 🔄 System Flow

### Complete Request Flow:

```
User Input (Text/Voice)
    ↓
[Voice] → Speech-to-Text → Cleaned Text
    ↓
Message Processor
    ↓
┌─────────────────────────────────────┐
│   PARALLEL AGENT PROCESSING         │
│   ┌──────────┐  ┌──────────┐       │
│   │ Emotion  │  │ Context  │       │
│   │  Agent   │  │  Agent   │       │
│   └──────────┘  └──────────┘       │
│        ┌──────────┐                 │
│        │   Task   │                 │
│        │  Agent   │                 │
│        └──────────┘                 │
└─────────────────────────────────────┘
    ↓
Agent Results Combined
    ↓
┌─────────────────────────────────────┐
│   PARALLEL MEMORY RETRIEVAL         │
│   Session | Sub-Temp | Temp | Perm  │
└─────────────────────────────────────┘
    ↓
Context Building
    ↓
AI Model (Anthropic/OpenAI)
    ↓
Response Generation
    ↓
Memory Storage (if important)
    ↓
Database Save (Message + Memory)
    ↓
[Voice] → Text-to-Speech
    ↓
User Receives Response
```

### Memory Management Flow:

```
New Information
    ↓
Importance Calculation
    ├─ Keywords detected
    ├─ Emotion intensity
    ├─ User emphasis
    └─ Context relevance
    ↓
Tier Assignment
    ├─ Score 0.9+ → Permanent
    ├─ Score 0.7+ → Temporary
    ├─ Score 0.5+ → Sub-Temporary
    └─ Score <0.5 → Session
    ↓
Storage with Expiry
    ↓
Background Optimization
    ├─ Cleanup expired
    ├─ Consolidate similar
    └─ Update importance
```

## 🚀 Making It More Advanced

### 1. **Enhanced AI Models**
```python
# Add more providers in config.json
"ai_models": {
  "providers": [
    {"name": "anthropic", "model": "claude-sonnet-4"},
    {"name": "openai", "model": "gpt-4"},
    {"name": "gemini", "model": "gemini-pro"},
    {"name": "local", "model": "llama-3"}
  ]
}
```

### 2. **Advanced Memory Features**
- **Semantic Search**: Use embeddings for similarity
- **Memory Graphs**: Connect related memories
- **Forgetting Curve**: Implement Ebbinghaus curve
- **Memory Consolidation**: Merge similar memories

```python
# memory/semantic_memory.py
from sentence_transformers import SentenceTransformer

class SemanticMemory:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def find_similar(self, query, memories, top_k=5):
        query_embedding = self.model.encode(query)
        memory_embeddings = self.model.encode([m.content for m in memories])
        similarities = cosine_similarity([query_embedding], memory_embeddings)
        return top_k_memories
```

### 3. **Personality System**
```python
# agents/personality_agent.py
class PersonalityAgent:
    def __init__(self, traits):
        self.traits = {
            'humor': 0.7,
            'empathy': 0.9,
            'curiosity': 0.8,
            'formality': 0.3
        }
    
    def adjust_response(self, response, context):
        # Modify response based on personality
        pass
```

### 4. **Proactive Features**
- **Reminder System**: Remind users of tasks
- **Conversation Initiator**: Start conversations
- **Mood Tracking**: Track user mood over time
- **Suggestion Engine**: Suggest topics

### 5. **Multi-Modal Support**
- **Image Understanding**: Process uploaded images
- **Document Analysis**: Read PDFs, documents
- **Web Browsing**: Search and summarize web content

### 6. **Advanced Voice**
- **Voice Cloning**: Custom voice output
- **Accent Detection**: Adapt to user accent
- **Emotion in Voice**: Emotional speech synthesis
- **Wake Word**: "Hey Friend" activation

### 7. **Learning System**
```python
# learning/preference_learner.py
class PreferenceLearner:
    def learn_from_interaction(self, user_message, response_feedback):
        # Learn user preferences over time
        # Adjust response style
        # Remember liked topics
        pass
```

### 8. **Context Awareness**
- **Time Awareness**: Know time of day, day of week
- **Location Awareness**: Use location context
- **Activity Context**: Understand what user is doing
- **Mood History**: Reference past emotional states

### 9. **Social Features**
- **Multi-User Support**: Different personalities per user
- **Shared Memories**: Group conversations
- **User Relationships**: Understand user connections

### 10. **Integration**
```python
# Add in config.json
"integrations": {
  "calendar": {"enabled": true, "api_key": "..."},
  "email": {"enabled": true, "smtp": "..."},
  "spotify": {"enabled": true, "token": "..."},
  "weather": {"enabled": true, "api_key": "..."}
}
```

## 📊 Performance Optimization

Current optimizations:
- ✅ Parallel agent processing (3 simultaneous)
- ✅ Async database operations
- ✅ Memory caching
- ✅ Query optimization with indexes
- ✅ Background cleanup tasks

Future optimizations:
- 🔄 Redis caching layer
- 🔄 Database connection pooling
- 🔄 Request queuing
- 🔄 Load balancing

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/test_database.py -v

# Test with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 🛡️ Security Considerations

- API keys stored in environment variables
- Input sanitization and validation
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting on API endpoints
- User data encryption (add if needed)

## 📈 Monitoring

```python
# Add monitoring in production
from prometheus_client import Counter, Histogram

request_counter = Counter('ai_friend_requests', 'Total requests')
response_time = Histogram('ai_friend_response_time', 'Response time')
```

## 🤝 Contributing

Areas for contribution:
1. Additional AI model providers
2. Advanced memory algorithms
3. New agent types
4. UI/Frontend development
5. Mobile app integration
6. Performance improvements

## 📝 License

MIT License - Free to use and modify!

## 🎉 Start Your AI Friend Journey!

The database will be automatically created on first run, or you can set it up manually for verification. Enjoy building meaningful AI relationships! 🚀
        
Authentication:
  POST   /api/auth/register
  POST   /api/auth/login
  POST   /api/auth/logout

Chat:
  POST   /api/chat/send
  GET    /api/chat/stream
  WS     /api/chat/ws/{user_id}
  GET    /api/chat/history
  DELETE /api/chat/clear

Memory:
  POST   /api/memory/save
  POST   /api/memory/search
  DELETE /api/memory/{memory_id}
  GET    /api/memory/stats

Voice:
  POST   /api/voice/stt
  POST   /api/voice/tts
  WS     /api/voice/stream/{user_id}
  GET    /api/voice/devices

Analytics:
  GET    /api/analytics/overview
  GET    /api/analytics/emotion-trends
  GET    /api/analytics/topics

Persona:
  GET    /api/persona/get
  POST   /api/persona/update
  POST   /api/persona/reset

Avatar:
  POST   /api/avatar/expression
  POST   /api/avatar/animation
  GET    /api/avatar/sync-speech

1. Change SECRET_KEY in auth/jwt_handler.py
2. Use PostgreSQL instead of SQLite
3. Configure proper CORS origins
4. Set up SSL/TLS
5. Use production Redis cluster
6. Deploy with Docker/Kubernetes
7. Add monitoring (Prometheus/Grafana)
8. Set up logging aggregation
9. Configure auto-scaling
10. Add CDN for audio files