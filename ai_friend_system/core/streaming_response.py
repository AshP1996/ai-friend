"""
Streaming response generator for real-time, human-like conversation
"""
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from .response_generator import ResponseGenerator
from utils.logger import Logger

logger = Logger("StreamingResponse")

class StreamingResponseGenerator:
    """Generate streaming responses token-by-token for natural conversation flow"""
    
    def __init__(self, response_generator: ResponseGenerator):
        self.response_generator = response_generator
        self.logger = Logger("StreamingResponse")
    
    async def stream_response(self, messages: List[Dict], context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Stream response tokens for real-time feel
        Yields words/phrases as they're generated
        """
        # For now, generate full response then stream it
        # In production, this would connect to streaming LLM APIs
        full_response = await self.response_generator.generate_response(messages, context)
        
        # Simulate natural human-like streaming
        words = full_response.split()
        
        # Stream with natural pauses (like human speech)
        for i, word in enumerate(words):
            yield word
            
            # Add micro-pauses at natural points
            if i < len(words) - 1:
                # Pause after punctuation
                if any(word.endswith(p) for p in ['.', '!', '?', ',']):
                    await asyncio.sleep(0.1)  # Natural pause
                # Pause every 5-7 words (breathing)
                elif (i + 1) % 6 == 0:
                    await asyncio.sleep(0.05)  # Micro pause
                else:
                    await asyncio.sleep(0.02)  # Minimal delay between words
