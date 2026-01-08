# Database Enhancement & Training Data Summary

## 🎯 Overview

The database has been completely enhanced to store comprehensive training data for future AI model training while maintaining flexibility and performance.

---

## 📊 Enhanced Database Schema

### 1. **Messages Table** - Enhanced with Training Data

**New Fields Added**:
- `context_embedding` (TEXT) - Full context embedding for training
- `agent_outputs` (TEXT/JSON) - Complete agent analysis results
- `memory_context` (TEXT/JSON) - Memories used in response
- `user_feedback` (REAL) - User rating (1-5 scale)
- `quality_score` (REAL) - Auto-calculated quality (0-1)
- `training_flag` (BOOLEAN) - Mark for training export
- `voice_pitch` (REAL) - Detected voice pitch (Hz)
- `voice_emotion` (TEXT) - Emotion detected from voice
- `audio_quality` (REAL) - Audio quality score

**Purpose**: Store complete conversation context for training custom AI models

---

### 2. **Conversations Table** - Analytics & Quality Tracking

**New Fields Added**:
- `total_messages` (INTEGER) - Total messages in conversation
- `avg_response_time` (REAL) - Average response time
- `avg_emotion_score` (REAL) - Average emotion confidence
- `conversation_quality` (REAL) - Overall quality score
- `user_satisfaction` (REAL) - User feedback average
- `topics_discussed` (TEXT/JSON) - Topics covered
- `training_data_exported` (BOOLEAN) - Export status
- `ended_at` (DATETIME) - Conversation end time

**Purpose**: Track conversation quality and analytics for training data selection

---

### 3. **Memories Table** - Enhanced Metadata

**New Fields Added**:
- `context` (TEXT) - Full context when memory was created
- `tags` (TEXT) - Comma-separated tags
- `emotion_at_creation` (TEXT) - Emotion when memory was stored
- `related_memories` (TEXT/JSON) - Related memory IDs
- `access_count` (INTEGER) - How many times accessed
- `training_relevance` (REAL) - Relevance for training
- `verified` (BOOLEAN) - Human verified flag

**Purpose**: Better memory organization and training data relevance

---

### 4. **Agent Logs Table** - Training Quality Tracking

**New Fields Added**:
- `conversation_id` (INTEGER) - Link to conversation
- `message_id` (INTEGER) - Link to message
- `confidence_score` (REAL) - Agent confidence
- `accuracy_score` (REAL) - Verified accuracy
- `training_quality` (REAL) - Quality for training

**Purpose**: Track agent performance for model improvement

---

## 🔧 Migration

### Run Migration Script

```bash
python database/migrate_schema.py
```

This script:
- ✅ Safely adds new columns to existing tables
- ✅ Preserves all existing data
- ✅ Handles columns that already exist
- ✅ Logs all changes

**Note**: Safe to run multiple times (idempotent)

---

## 📈 Training Data Export

### Export API Endpoints

**1. Export Single Conversation**
```bash
POST /api/training/export
{
  "conversation_id": 123,
  "format": "json"
}
```

**2. Export All Conversations**
```bash
POST /api/training/export
{
  "limit": 100,
  "format": "json"
}
```

**3. Get Training Stats**
```bash
GET /api/training/stats
```

**4. Mark as Exported**
```bash
POST /api/training/mark-exported/{conversation_id}
```

### Export Format

```json
{
  "conversation_id": 123,
  "session_id": "uuid",
  "user_id": "user123",
  "metadata": {
    "model_used": "ollama",
    "total_messages": 45,
    "avg_response_time": 1.5,
    "conversation_quality": 0.8,
    "topics_discussed": ["work", "hobbies"]
  },
  "messages": [
    {
      "role": "user",
      "content": "Hello!",
      "emotion": "happy",
      "voice_pitch": 180.5,
      "agent_outputs": {...},
      "quality_score": 0.85
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "emotion": "happy",
      "processing_time": 1.2,
      "memory_context": [...],
      "quality_score": 0.9
    }
  ],
  "memories": [...],
  "agent_logs": [...]
}
```

---

## 🧠 Enhanced Memory Management

### Memory Storage Improvements

1. **Context Preservation**: Full context saved with each memory
2. **Emotion Tracking**: Emotion at creation time stored
3. **Relationship Mapping**: Related memories linked
4. **Access Tracking**: Access count and last accessed time
5. **Training Relevance**: Relevance score for training data selection
6. **Verification Flag**: Human-verified memories marked

### Memory Retrieval Optimization

- **Parallel Tier Retrieval**: All tiers queried simultaneously
- **Strict Limits**: Max 5 memories total (2 per tier)
- **Batch Updates**: Memory access counts updated in batch
- **Non-blocking**: Updates happen in background

---

## 🎤 Voice Streaming Fix

### Issue Fixed
- **Problem**: Voice streaming only returned partial transcriptions, never final
- **Solution**: Added silence detection with 1-second timeout

### How It Works

1. **Pitch Analysis**: Real-time pitch detection from PCM
2. **Silence Detection**: Detects silence periods (>1 second)
3. **Final Trigger**: Returns final transcription after silence
4. **Voice Data Storage**: Pitch, emotion, quality saved to database

### Voice Data Saved

- User messages include:
  - `voice_pitch`: Detected pitch (Hz)
  - `voice_emotion`: Emotion from voice analysis
  - `audio_quality`: Energy/quality score

---

## 📊 Quality Score Calculation

### Auto-Calculated Quality Metrics

**Factors**:
1. Response length (optimal 20-100 words): +0.1
2. Processing time (0.5-3s optimal): +0.1
3. Emotion confidence: +0.2 × (confidence - 0.5)
4. Memory usage (1-5 memories): +0.1

**Score Range**: 0.0 to 1.0

**Usage**: Filter high-quality conversations for training

---

## 🔄 Data Flow for Training

```
User Interaction
    ↓
Message Saved (with all metadata)
    ├─→ Agent outputs (JSON)
    ├─→ Memory context (JSON)
    ├─→ Voice data (if voice)
    └─→ Quality score (auto-calculated)
    ↓
Conversation Stats Updated
    ├─→ Total messages
    ├─→ Avg response time
    ├─→ Avg emotion score
    └─→ Conversation quality
    ↓
Training Flag Set (default: true)
    ↓
Export via API
    ├─→ Full conversation data
    ├─→ All messages with context
    ├─→ All memories
    └─→ All agent logs
    ↓
Mark as Exported
```

---

## 💾 Database Flexibility

### Flexible JSON Storage

- **Agent Outputs**: Complete agent analysis stored as JSON
- **Memory Context**: Memory arrays stored as JSON
- **Topics**: Topics array stored as JSON
- **Related Memories**: Memory relationships as JSON

### Benefits

1. **Easy Querying**: SQL queries on structured data
2. **Training Ready**: Direct export to training formats
3. **Extensible**: Add new fields without schema changes
4. **Backward Compatible**: Existing data preserved

---

## 🚀 Usage for Training

### Step 1: Collect Data
- Conversations automatically marked for training
- Quality scores calculated automatically
- All metadata stored

### Step 2: Export Data
```python
# Export high-quality conversations
POST /api/training/export
{
  "limit": 1000,
  "format": "json"
}
```

### Step 3: Filter by Quality
```python
# In exported data, filter by quality_score
high_quality = [c for c in data if c['metadata']['conversation_quality'] > 0.7]
```

### Step 4: Train Model
- Use exported JSON for fine-tuning
- Include context embeddings
- Use agent outputs for multi-task learning
- Use voice data for multimodal training

---

## 📋 Database Indexes

**Optimized Indexes Added**:
- `messages.conversation_id` - Fast message retrieval
- `messages.emotion` - Emotion-based queries
- `messages.role` - Role-based filtering
- `memories.tier` - Tier-based queries
- `memories.importance` - Importance sorting
- `memories.access_count` - Access tracking
- `conversations.platform` - Platform analytics
- `conversations.is_active` - Active conversation queries

---

## 🔍 Query Examples

### Get High-Quality Conversations
```sql
SELECT * FROM conversations 
WHERE conversation_quality > 0.7 
AND training_data_exported = 0
ORDER BY conversation_quality DESC
LIMIT 100;
```

### Get Messages with Voice Data
```sql
SELECT * FROM messages 
WHERE voice_pitch IS NOT NULL
AND training_flag = 1;
```

### Get Memories by Relevance
```sql
SELECT * FROM memories 
WHERE training_relevance > 0.8
ORDER BY importance DESC, access_count DESC;
```

---

## ✅ Benefits

1. **Training Ready**: All data structured for AI training
2. **Flexible**: JSON fields allow schema evolution
3. **Comprehensive**: Every detail stored
4. **Performant**: Indexed for fast queries
5. **Exportable**: Easy export via API
6. **Quality Filtered**: Auto-quality scoring
7. **Voice Data**: Pitch and emotion from voice
8. **Context Rich**: Full context preserved

---

## 🎯 Future Training Use Cases

1. **Fine-tune LLM**: Use conversation pairs
2. **Emotion Model**: Train on emotion data
3. **Voice Model**: Train on pitch/emotion patterns
4. **Memory Model**: Train on memory relationships
5. **Quality Model**: Train on quality scores
6. **Multi-modal**: Combine text + voice data

---

**Migration Required**: Run `python database/migrate_schema.py` to add new columns

**Backward Compatible**: Existing data preserved, new fields nullable
