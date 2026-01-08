# Voice Streaming Protocol

## Message Flow

When a user speaks via voice, the WebSocket sends/receives messages in this order:

### 1. **Partial Transcription** (Real-time)
```json
{
  "type": "partial",
  "text": "Hello how are..."
}
```
- Sent continuously as user speaks
- Shows real-time transcription

### 2. **Status: Thinking**
```json
{
  "type": "status",
  "state": "thinking",
  "text": "Hello how are you?",
  "emotion": "happy"
}
```
- Sent when final transcription is received
- Includes user's transcribed text and detected emotion

### 3. **Text Response**
```json
{
  "type": "response",
  "text": "I'm doing great! How about you?",
  "emotion": "happy",
  "has_audio": true
}
```
- **This is the TEXT response** - always sent
- `has_audio: true` indicates audio is coming next

### 4. **Status: Speaking**
```json
{
  "type": "status",
  "state": "speaking"
}
```
- Indicates audio generation has started

### 5. **Audio Start**
```json
{
  "type": "audio_start",
  "size": 123456,
  "format": "wav"
}
```
- Indicates audio chunks are about to be sent
- `size`: Total audio size in bytes
- `format`: Audio format (wav)

### 6. **Audio Chunks** (Binary)
- Binary WAV data sent in chunks (4KB each)
- Multiple `send_bytes()` calls
- Frontend should accumulate these chunks

### 7. **Audio End**
```json
{
  "type": "audio_end",
  "total_bytes": 123456
}
```
- Indicates all audio chunks have been sent
- Frontend can now play the complete audio

### 8. **Status: Listening**
```json
{
  "type": "status",
  "state": "listening"
}
```
- Ready for next voice input

## Frontend Implementation

### Example JavaScript Handler

```javascript
const ws = new WebSocket('ws://localhost:8000/api/voice/stream/user123');

let audioChunks = [];
let audioBuffer = null;

ws.onmessage = async (event) => {
  // Check if binary (audio) or text (JSON)
  if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
    // Audio chunk - accumulate
    const chunk = await event.data.arrayBuffer();
    audioChunks.push(chunk);
  } else {
    // JSON message
    const message = JSON.parse(event.data);
    
    switch (message.type) {
      case 'partial':
        // Show partial transcription
        updatePartialText(message.text);
        break;
        
      case 'response':
        // Show text response
        displayTextResponse(message.text);
        // Prepare for audio
        audioChunks = [];
        break;
        
      case 'audio_start':
        // Reset audio buffer
        audioChunks = [];
        console.log(`Audio incoming: ${message.size} bytes`);
        break;
        
      case 'audio_end':
        // Combine all chunks and play
        const totalSize = message.total_bytes;
        const combined = new Uint8Array(totalSize);
        let offset = 0;
        
        for (const chunk of audioChunks) {
          combined.set(new Uint8Array(chunk), offset);
          offset += chunk.byteLength;
        }
        
        // Create audio blob and play
        const audioBlob = new Blob([combined], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        
        // Cleanup
        audioChunks = [];
        break;
        
      case 'status':
        updateStatus(message.state);
        break;
        
      case 'error':
        console.error('Error:', message.message);
        break;
    }
  }
};
```

## Error Handling

If audio generation fails:
```json
{
  "type": "error",
  "message": "Audio generation failed: [error details]"
}
```

The text response is still available even if audio fails.

## Complete Example Flow

```
User speaks: "Hello"
  ↓
[Partial] "Hello"
  ↓
[Status] thinking
  ↓
[Response] "Hi there! How can I help you?" (TEXT)
  ↓
[Status] speaking
  ↓
[Audio Start] size: 45678
  ↓
[Binary] chunk 1 (4096 bytes)
[Binary] chunk 2 (4096 bytes)
...
[Binary] chunk N (last chunk)
  ↓
[Audio End] total_bytes: 45678
  ↓
[Status] listening
```

## Key Points

1. **Text is ALWAYS sent first** - even if audio fails
2. **Audio is sent in binary chunks** - accumulate before playing
3. **Audio format is WAV** - 16kHz, mono
4. **Both text and audio are sent** - frontend can show text while audio plays
5. **Error handling** - text response always available as fallback
