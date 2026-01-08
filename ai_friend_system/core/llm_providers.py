import asyncio
import threading
import requests
from typing import Optional, List, Dict, Any
from utils.logger import Logger
from config import settings

# class OllamaProvider:
#     '''Free local LLM using Ollama - No API key needed!'''
    
#     def __init__(self):
#         self.logger = Logger("Ollama")
#         self.api_url = settings.get('ai_models.primary.api_url', 'http://localhost:11434')
#         self.model = settings.get('ai_models.primary.model', 'llama2')
#         self.available = False
#         self._check_availability()
    
#     def _check_availability(self):            
#         '''Check if Ollama is running'''
#         try:
#             response = requests.get(f"{self.api_url}/api/tags", timeout=2)
#             if response.status_code == 200:
#                 self.available = True
#                 self.logger.info("Ollama is available")
#             else:
#                 self.logger.warning("Ollama is not responding")
#         except Exception as e:
#             self.logger.warning(f"Ollama not available: {e}")
#             self.available = False
    
#     async def generate(self, messages: List[Dict], system_prompt: str) -> Optional[str]:
#         '''Generate response using Ollama'''
#         if not self.available:
#             return None
        
#         try:
#             # Convert messages to prompt
#             prompt = self._build_prompt(messages, system_prompt)
            
#             # Call Ollama API
#             response = await asyncio.to_thread(
#                 requests.post,
#                 f"{self.api_url}/api/generate",
#                 json={
#                     "model": self.model,
#                     "prompt": prompt,
#                     "stream": False
#                 },
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 return result.get('response', '').strip()
#             else:
#                 self.logger.error(f"Ollama error: {response.status_code}")
#                 return None
                
#         except Exception as e:
#             self.logger.error(f"Ollama generation error: {e}")
#             return None
    
#     def _build_prompt(self, messages: List[Dict], system_prompt: str) -> str:
#         '''Build prompt from messages'''
#         prompt = f"System: {system_prompt}\\n\\n"
        
#         for msg in messages:
#             role = msg.get('role', 'user')
#             content = msg.get('content', '')
#             prompt += f"{role.capitalize()}: {content}\\n"
        
#         prompt += "Assistant:"
#         return prompt

class OllamaProvider:
    '''Free local LLM using Ollama (phi)'''

    def __init__(self):
        self.logger = Logger("Ollama")
        self.api_url = settings.get(
            'ai_models.primary.api_url',
            'http://localhost:11434'
        )
        self.model = settings.get(
            'ai_models.primary.model',
            'phi:latest'   # ✅ EXACT name
        )
        self.available = False
        self._check_availability()

    def _check_availability(self):
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=1)  # Faster timeout
            if response.status_code == 200:
                self.available = True
                self.logger.debug("Ollama server reachable")
            else:
                self.available = False
        except Exception:
            self.available = False

    async def generate(self, messages, system_prompt):
        if not self.available:
            return None

        try:
            prompt = self._build_prompt(messages, system_prompt)

            response = await asyncio.to_thread(
                requests.post,
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 400,  # Increased for detailed, natural responses
                        "temperature": 0.8,  # More creative and natural
                        "top_p": 0.9,
                        "repeat_penalty": 1.1  # Reduce repetition
                    }
                },
                timeout=10  # Increased timeout for better responses
            )

            if response.status_code == 200:
                return response.json().get("response", "").strip()

            return None

        except Exception:
            return None  # Silent fail for speed

    def _build_prompt(self, messages, system_prompt):
        prompt = f"System: {system_prompt}\n\n"
        for msg in messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        prompt += "Assistant:"
        return prompt


class HuggingFaceProvider:
    '''Free Hugging Face models - No API key needed!
    
    SHARED MODEL: Model is loaded once and shared across all instances.
    Each instance references the shared model.
    '''
    _instance = None
    _model = None
    _tokenizer = None
    _lock = threading.Lock()
    _logger = Logger("HuggingFace")
    _model_loaded = False
    
    def __new__(cls):
        """Singleton pattern - only one provider instance"""
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
            self.model_name = settings.get('ai_models.fallback.model', 'microsoft/DialoGPT-medium')
            self.available = False
            
            # Load model only once (shared across all instances)
            if not self.__class__._model_loaded:
                self._load_model()
            else:
                # Use shared model
                self.model = self.__class__._model
                self.tokenizer = self.__class__._tokenizer
                self.available = True
            
            self._initialized = True
    
    def _load_model(self):
        '''Load HuggingFace model (only once)'''
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self.logger.info(f"Loading model: {self.model_name} (shared, one-time load)...")
            self.__class__._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.__class__._model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.__class__._tokenizer.padding_side = 'left'  # Fix for decoder-only models
            self.__class__._model_loaded = True
            
            # Set instance references
            self.tokenizer = self.__class__._tokenizer
            self.model = self.__class__._model
            self.available = True
            self.logger.info("✅ HuggingFace model loaded (will be shared across all instances)")
        except Exception as e:
            self.logger.error(f"Failed to load HuggingFace model: {e}")
            self.available = False
    
    async def generate(self, messages: List[Dict], system_prompt: str) -> Optional[str]:
        '''Generate response using HuggingFace model'''
        if not self.available:
            return None
        
        try:
            # Get last user message
            user_message = messages[-1].get('content', '') if messages else ''
            
            # Ensure tokenizer padding_side is set correctly (fix warning)
            if self.tokenizer.padding_side != 'left':
                self.tokenizer.padding_side = 'left'
            
            # Build full conversation context for better responses
            conversation_text = ""
            for msg in messages[-3:]:  # Last 3 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'user':
                    conversation_text += f"User: {content}\n"
                elif role == 'assistant':
                    conversation_text += f"Assistant: {content}\n"
            
            # Add system prompt context
            if system_prompt:
                conversation_text = f"{system_prompt}\n\n{conversation_text}"
            
            conversation_text += "Assistant:"
            
            # Encode full context
            inputs = self.tokenizer.encode(conversation_text, return_tensors='pt', max_length=512, truncation=True)
            input_length = inputs.shape[-1]
            
            # Generate response with max_new_tokens for longer outputs
            outputs = await asyncio.to_thread(
                self.model.generate,
                inputs,
                max_new_tokens=150,  # Generate up to 150 new tokens (not total length)
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.85,  # More creative and natural
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.15,  # Reduce repetition
                no_repeat_ngram_size=3  # Prevent 3-gram repetition
            )
            
            # Decode only the new tokens (response)
            response = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
            response = response.strip()
            
            # Ensure minimum length - if too short, add more context
            if len(response.split()) < 10:
                self.logger.warning(f"Response too short ({len(response.split())} words), regenerating...")
                # Try again with more aggressive parameters
                outputs = await asyncio.to_thread(
                    self.model.generate,
                    inputs,
                    max_new_tokens=200,
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.9,
                    top_p=0.95,
                    repetition_penalty=1.1
                )
                response = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True).strip()
            
            self.logger.info(f"HuggingFace generated {len(response.split())} words: {response[:100]}...")
            return response
            
        except Exception as e:
            self.logger.error(f"HuggingFace generation error: {e}")
            return None


class SimpleChatbot:
    '''Simple rule-based chatbot - Always works!'''
    
    def __init__(self):
        self.logger = Logger("SimpleChatbot")
        self.patterns = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'how_are_you': ['how are you', 'how do you do', 'how are things'],
            'name': ['what is your name', 'who are you', 'your name'],
            'help': ['help', 'assist', 'support'],
            'thanks': ['thank', 'thanks', 'appreciate'],
            'goodbye': ['bye', 'goodbye', 'see you', 'farewell'],
        }
        
        self.responses = {
            'greeting': [
                "Hello! I'm so happy to chat with you! 😊",
                "Hi there! How can I help you today?",
                "Hey! Great to see you! What's on your mind?"
            ],
            'how_are_you': [
                "I'm doing great, thank you for asking! How about you?",
                "I'm wonderful! Ready to chat and help however I can!",
                "I'm having a great day! How are you feeling?"
            ],
            'name': [
                "I'm your AI friend! You can call me Friend. What's your name?",
                "I'm an AI companion here to chat with you! What would you like to talk about?",
                "I'm your friendly AI assistant! How can I help you today?"
            ],
            'help': [
                "I'm here to chat, listen, and help! Just tell me what's on your mind.",
                "I can chat about anything you'd like! Ask me questions, share your thoughts, or just talk.",
                "I'm happy to help! What would you like to talk about?"
            ],
            'thanks': [
                "You're very welcome! I'm happy to help! 😊",
                "My pleasure! Feel free to chat anytime!",
                "You're welcome! I'm here whenever you need me!"
            ],
            'goodbye': [
                "Goodbye! It was great chatting with you! Come back soon! 👋",
                "See you later! Take care! 😊",
                "Farewell! Looking forward to our next chat!"
            ],
            'default': [
                "That's interesting! Tell me more about that.",
                "I hear what you're saying. How does that make you feel?",
                "Thanks for sharing that with me! What else is on your mind?",
                "I'm listening! Please continue.",
                "That's really something! What do you think about it?",
                "I understand. Is there anything specific you'd like to discuss?",
                "Interesting perspective! What led you to think that way?"
            ]
        }
    
    async def generate(self, messages: List[Dict], system_prompt: str) -> str:
        '''Generate simple rule-based response'''
        import random
        
        if not messages:
            return random.choice(self.responses['greeting'])
        
        # Get last user message
        user_message = messages[-1].get('content', '').lower()
        
        # Check patterns
        for pattern_name, keywords in self.patterns.items():
            if any(keyword in user_message for keyword in keywords):
                return random.choice(self.responses.get(pattern_name, self.responses['default']))
        
        # Check for questions
        if '?' in user_message:
            question_responses = [
                "That's a great question! Let me think...",
                "Hmm, interesting question! From what I understand...",
                "Good question! Here's what I think...",
            ]
            return random.choice(question_responses) + " " + random.choice(self.responses['default'])
        
        # Default response
        return random.choice(self.responses['default'])