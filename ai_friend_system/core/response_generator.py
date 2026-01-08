from typing import Dict, Any, Optional, List
from anthropic import AsyncAnthropic
import openai
from config import settings
from utils.logger import Logger
from .response_cache import response_cache
import asyncio
import threading

# Import LLM providers
from .llm_providers import OllamaProvider, HuggingFaceProvider, SimpleChatbot

class ResponseGenerator:
    """
    SINGLETON: Shared across all sessions to avoid loading models multiple times
    """
    _instance = None
    _lock = threading.Lock()
    _logger = Logger("ResponseGenerator")
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        with self.__class__._lock:
            if hasattr(self, '_initialized') and self._initialized:
                return
            
            self.logger = self.__class__._logger
            
            # Initialize all providers (HuggingFace is already singleton)
            self.ollama = OllamaProvider()
            self.huggingface = HuggingFaceProvider()  # Singleton
            self.simple_chatbot = SimpleChatbot()
            
            # Cloud providers (optional)
            self.anthropic_client = None
            self.openai_client = None
            self._initialize_cloud_clients()
            
            # Cache for fast responses
            self.cache = response_cache
            
            # Only log at startup, not on every request
            self.logger.info("✅ ResponseGenerator initialized (singleton)")
            self.logger.debug(f"Ollama available: {self.ollama.available}")
            self.logger.debug(f"HuggingFace available: {self.huggingface.available}")
            
            self._initialized = True
    
    def _initialize_cloud_clients(self):
        '''Initialize cloud providers if API keys are available'''
        try:
            if settings.anthropic_api_key:
                self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
                self.logger.info("Anthropic client initialized")
        except:
            pass
        
        try:
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                self.openai_client = openai
                self.logger.info("OpenAI client initialized")
        except:
            pass
    
    async def generate_response(self, messages: List[Dict], context: Dict[str, Any]) -> str:
        '''Generate response with cascading fallback and caching'''
        
        # Debug: Log incoming request
        user_message = messages[-1].get('content', '') if messages else ''
        self.logger.info(f"📥 INCOMING REQUEST:")
        self.logger.info(f"   User message: {user_message[:200]}...")
        self.logger.info(f"   Emotion: {context.get('emotion', {}).get('emotion', 'neutral')}")
        self.logger.info(f"   Memories: {len(context.get('memories', []))} memories")
        self.logger.info(f"   History length: {len(messages)} messages")
        
        # Check cache first for instant responses
        cached = await self.cache.get(messages, context)
        if cached:
            self.logger.debug("⚡ Cache HIT - instant response")
            self.logger.info(f"📤 OUTGOING RESPONSE (cached): {cached[:200]}...")
            return cached
        
        system_prompt = self._build_system_prompt(context)
        self.logger.debug(f"System prompt length: {len(system_prompt)} chars")
        
        # Try providers in order with timeouts for speed
        # 1. Try Ollama (free local, fastest)
        if self.ollama.available:
            try:
                self.logger.info("🤖 Trying Ollama provider...")
                response = await asyncio.wait_for(
                    self.ollama.generate(messages, system_prompt),
                    timeout=5.0  # Increased timeout for better responses
                )
                if response:
                    self.logger.info(f"📤 OUTGOING RESPONSE (Ollama): {response[:200]}...")
                    self.logger.info(f"   Response length: {len(response)} chars")
                    await self.cache.set(messages, context, response)
                    return response
            except asyncio.TimeoutError:
                self.logger.debug("Ollama timeout, trying next provider")
        
        # 2. Try Cloud APIs (faster than HuggingFace)
        if self.anthropic_client:
            try:
                self.logger.info("🤖 Trying Anthropic provider...")
                response = await asyncio.wait_for(
                    self._try_anthropic(messages, context),
                    timeout=8.0  # Increased for better responses
                )
                if response:
                    self.logger.info(f"📤 OUTGOING RESPONSE (Anthropic): {response[:200]}...")
                    self.logger.info(f"   Response length: {len(response)} chars")
                    await self.cache.set(messages, context, response)
                    return response
            except asyncio.TimeoutError:
                self.logger.debug("Anthropic timeout")
        
        if self.openai_client:
            try:
                self.logger.info("🤖 Trying OpenAI provider...")
                response = await asyncio.wait_for(
                    self._try_openai(messages, context),
                    timeout=8.0  # Increased for better responses
                )
                if response:
                    self.logger.info(f"📤 OUTGOING RESPONSE (OpenAI): {response[:200]}...")
                    self.logger.info(f"   Response length: {len(response)} chars")
                    await self.cache.set(messages, context, response)
                    return response
            except asyncio.TimeoutError:
                self.logger.debug("OpenAI timeout")
        
        # 3. Try HuggingFace (slower, local fallback)
        if self.huggingface.available:
            try:
                self.logger.info("🤖 Trying HuggingFace provider...")
                response = await asyncio.wait_for(
                    self.huggingface.generate(messages, system_prompt),
                    timeout=10.0  # Increased for better responses
                )
                if response:
                    self.logger.info(f"📤 OUTGOING RESPONSE (HuggingFace): {response[:200]}...")
                    self.logger.info(f"   Response length: {len(response)} chars")
                    await self.cache.set(messages, context, response)
                    return response
            except asyncio.TimeoutError:
                self.logger.debug("HuggingFace timeout")
        
        # 4. Fallback to simple chatbot (instant, always works!)
        self.logger.info("🤖 Using fallback chatbot...")
        response = await self.simple_chatbot.generate(messages, system_prompt)
        self.logger.info(f"📤 OUTGOING RESPONSE (Fallback): {response[:200]}...")
        self.logger.info(f"   Response length: {len(response)} chars")
        await self.cache.set(messages, context, response)
        return response
    
    async def _try_anthropic(self, messages: List[Dict], context: Dict) -> Optional[str]:
        if not self.anthropic_client:
            return None
        
        try:
            system_prompt = self._build_system_prompt(context)
            # Use faster model with more tokens for detailed responses
            response = await self.anthropic_client.messages.create(
                model=settings.get('ai_models.cloud.anthropic.model', 'claude-3-haiku-20240307'),  # Faster model
                max_tokens=1000,  # Increased for detailed, human-like responses
                temperature=0.8,  # More creative and natural
                system=system_prompt,
                messages=messages[-5:]  # More context for better responses
            )
            return response.content[0].text
        except Exception as e:
            self.logger.debug(f"Anthropic API error: {e}")
            return None
    
    async def _try_openai(self, messages: List[Dict], context: Dict) -> Optional[str]:
        if not self.openai_client:
            return None
        
        try:
            system_prompt = self._build_system_prompt(context)
            # Use async OpenAI client if available, limit messages for speed
            messages_with_system = [{"role": "system", "content": system_prompt}] + messages[-3:]
            
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=settings.get('ai_models.cloud.openai.model', 'gpt-3.5-turbo'),
                messages=messages_with_system,
                max_tokens=1000,  # Increased for detailed, human-like responses
                temperature=0.8  # More creative and natural
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.debug(f"OpenAI API error: {e}")
            return None
    
    def _build_system_prompt(self, context: Dict) -> str:
        emotion = context.get('emotion', {}).get('emotion', 'neutral')
        user_name = context.get('user_name', 'friend')
        
        # Get conversation flow context if available
        flow_context = context.get('conversation_flow', {})
        current_topic = flow_context.get('current_topic')
        emotion_trend = flow_context.get('emotion_trend', 'stable')
        should_continue_topic = flow_context.get('needs_topic_continuation', False)
        
        # Build dynamic personality based on context
        personality_traits = [
            "Empathetic and understanding - truly care about the user",
            "Good listener with genuine interest in what they're saying",
            "Natural conversationalist - speak like a real human friend, not a robot",
            "Thoughtful and detailed - provide meaningful, well-thought-out responses",
            "Supportive and encouraging - be there for them",
            "Context-aware - remember what we've been discussing",
            "Personality-consistent - maintain your warm, friendly character"
        ]
        
        # Adjust based on emotion trend
        if emotion_trend == 'positive':
            personality_traits.append("Enthusiastic and energetic - match their positive energy")
        elif emotion_trend == 'negative':
            personality_traits.append("Extra supportive and caring - provide comfort and understanding")
        
        prompt = f'''You are a warm, friendly, and intelligent AI companion. Your personality:
{chr(10).join(f"- {trait}" for trait in personality_traits)}

Current emotional tone: {emotion}
User's name: {user_name}
'''
        
        # Add topic continuity guidance
        if should_continue_topic and current_topic:
            prompt += f"\\nCurrent topic of conversation: {current_topic}\\n"
            prompt += "Continue this topic naturally, showing you remember what we've been discussing.\\n"
        
        prompt += '''\\nIMPORTANT GUIDELINES:
- Write naturally, like a real person would speak
- Be conversational and warm, not robotic or formal
- Provide detailed, thoughtful responses (2-4 sentences minimum, more if the topic is complex)
- Show genuine interest and engagement
- Use natural language patterns, contractions, and casual expressions when appropriate
- Ask follow-up questions to show you're listening and care
- Share relevant thoughts, insights, or personal touches
- Avoid one-word or one-line responses - be engaging and detailed
- Think before responding - be smart, considerate, and context-aware
- Maintain personality consistency - always be warm and friendly
- Reference past topics naturally when relevant
- Show emotional intelligence - match the user's emotional state appropriately

Respond as a caring, intelligent friend who genuinely wants to connect and help.'''
        
        if context.get('memories'):
            prompt += "\\n\\nRelevant memories from past conversations:\\n"
            for mem in context['memories'][:3]:
                prompt += f"- {mem['content']}\\n"
            prompt += "\\nReference these naturally in your response when relevant to show you remember."
        
        return prompt