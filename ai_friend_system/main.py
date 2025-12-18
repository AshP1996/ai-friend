import asyncio
import argparse
from core.lifecycle import SystemLifecycle
from core import AIFriend
from utils.logger import Logger

logger = Logger("Main")

async def interactive_mode():
    await SystemLifecycle.startup()
    ai_friend = AIFriend()
    await ai_friend.initialize()
    print("=" * 60)
    print("AI FRIEND SYSTEM - Interactive Mode")
    print("=" * 60)
    
    logger.info("Initializing AI Friend...")
    await ai_friend.initialize()
    await ai_friend.start_conversation()
    
    print("\nAI Friend is ready!")
    print("Commands:")
    print("  'voice' - Switch to voice mode")
    print("  'text' - Switch to text mode")
    print("  'summary' - Show conversation summary")
    print("  'quit' - Exit")
    print("\nType your message or command:\n")
    
    mode = "text"
    
    while True:
        try:
            if mode == "text":
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("Goodbye! 👋")
                    break
                elif user_input.lower() == 'voice':
                    mode = "voice"
                    print("Switched to voice mode.")
                    continue
                elif user_input.lower() == 'summary':
                    summary = await ai_friend.get_conversation_summary()
                    stats = summary.get('stats', {})
                    print(f"\nMessages: {stats.get('message_count', 0)}")
                    print(f"Avg Processing: {stats.get('avg_processing_time', 0):.3f}s\n")
                    continue
                
                # Process text message - WITH SAFE ERROR HANDLING
                result = await ai_friend.chat(user_input)
                
                # Safe access to all fields
                response = result.get('response', 'I am here!')
                emotion_data = result.get('emotion', {})
                
                if isinstance(emotion_data, dict):
                    emotion = emotion_data.get('emotion', 'neutral')
                else:
                    emotion = 'neutral'
                
                processing_time = result.get('processing_time', 0)
                memories_used = result.get('memories_used', 0)
                
                print(f"\nAI Friend [{emotion}]: {response}")
                print(f"[⚡ {processing_time:.2f}s | 🧠 {memories_used} memories]\n")
            
            else:  # voice mode
                text_check = input("(Press Enter to listen, or 'text' to switch): ").strip()
                
                if text_check.lower() == 'text':
                    mode = "text"
                    print("Switched to text mode.")
                    continue
                
                print("\n🎤 Listening...")
                result = await ai_friend.voice_chat(listen_timeout=5)
                
                if result:
                    response = result.get('response', 'I heard you!')
                    print(f"\n🔊 AI Friend: {response}\n")
                else:
                    print("No speech detected. Try again.\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Oops! Something went wrong. Let's try again.\n")

async def api_mode(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    from api import app
    
    logger.info(f"Starting API server on {host}:{port}")
    print(f"\n🚀 AI Friend API Server")
    print(f"📡 http://{host}:{port}")
    print(f"📚 http://{host}:{port}/docs\n")
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

def main():
    parser = argparse.ArgumentParser(description="AI Friend System")
    parser.add_argument('--mode', choices=['interactive', 'api'], default='interactive')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8000)
    
    args = parser.parse_args()
    
    if args.mode == 'interactive':
        asyncio.run(interactive_mode())
    else:
        asyncio.run(api_mode(args.host, args.port))

if __name__ == "__main__":
    main()
