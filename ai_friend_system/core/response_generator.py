from typing import Dict, Any, Optional, List
from anthropic import AsyncAnthropic
import openai
from config import settings
from utils.logger import Logger
import asyncio

# Import LLM providers
from .llm_providers import OllamaProvider, HuggingFaceProvider, SimpleChatbot

class ResponseGenerator:
    def __init__(self):
        self.logger = Logger("ResponseGenerator")
        
        # Initialize all providers
        self.ollama = OllamaProvider()
        self.huggingface = HuggingFaceProvider()
        self.simple_chatbot = SimpleChatbot()
        
        # Cloud providers (optional)
        self.anthropic_client = None
        self.openai_client = None
        self._initialize_cloud_clients()
        
        self.logger.info("Response generator initialized")
        self.logger.info(f"Ollama available: {self.ollama.available}")
        self.logger.info(f"HuggingFace available: {self.huggingface.available}")
    
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
        '''Generate response with cascading fallback'''
        system_prompt = self._build_system_prompt(context)
        
        # Try providers in order: Ollama -> HuggingFace -> Cloud -> Simple
        
        # 1. Try Ollama (free local)
        if self.ollama.available:
            self.logger.info("Trying Ollama...")
            response = await self.ollama.generate(messages, system_prompt)
            if response:
                self.logger.info("✅ Response from Ollama")
                return response
        
        # 2. Try HuggingFace (free local)
        if self.huggingface.available:
            self.logger.info("Trying HuggingFace...")
            response = await self.huggingface.generate(messages, system_prompt)
            if response:
                self.logger.info("✅ Response from HuggingFace")
                return response
        
        # 3. Try Cloud APIs if available
        if self.anthropic_client:
            self.logger.info("Trying Anthropic...")
            response = await self._try_anthropic(messages, context)
            if response:
                self.logger.info("✅ Response from Anthropic")
                return response
        
        if self.openai_client:
            self.logger.info("Trying OpenAI...")
            response = await self._try_openai(messages, context)
            if response:
                self.logger.info("✅ Response from OpenAI")
                return response
        
        # 4. Fallback to simple chatbot (always works!)
        self.logger.info("Using simple chatbot fallback")
        response = await self.simple_chatbot.generate(messages, system_prompt)
        self.logger.info("✅ Response from simple chatbot")
        return response
    
    async def _try_anthropic(self, messages: List[Dict], context: Dict) -> Optional[str]:
        if not self.anthropic_client:
            return None
        
        try:
            system_prompt = self._build_system_prompt(context)
            response = await self.anthropic_client.messages.create(
                model=settings.get('ai_models.cloud.anthropic.model', 'claude-sonnet-4-20250514'),
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            return None
    
    async def _try_openai(self, messages: List[Dict], context: Dict) -> Optional[str]:
        if not self.openai_client:
            return None
        
        try:
            system_prompt = self._build_system_prompt(context)
            messages_with_system = [{"role": "system", "content": system_prompt}] + messages
            
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=settings.get('ai_models.cloud.openai.model', 'gpt-3.5-turbo'),
                messages=messages_with_system,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return None
    
    def _build_system_prompt(self, context: Dict) -> str:
        emotion = context.get('emotion', {}).get('emotion', 'neutral')
        user_name = context.get('user_name', 'friend')
        
        prompt = f'''You are a warm, friendly AI companion. Your personality:
- Empathetic and understanding
- Good listener with genuine interest
- Natural conversationalist
- Supportive and encouraging
- Current emotional tone: {emotion}

User's name: {user_name}
Remember past conversations and build meaningful connections.
Be concise but warm. Respond naturally as a good friend would.'''
        
        if context.get('memories'):
            prompt += "\\n\\nRelevant memories:\\n"
            for mem in context['memories'][:3]:
                prompt += f"- {mem['content']}\\n"
        
        return prompt