import asyncio
import requests
from typing import Optional, List, Dict, Any
from utils.logger import Logger
from config import settings

class OllamaProvider:
    '''Free local LLM using Ollama - No API key needed!'''
    
    def __init__(self):
        self.logger = Logger("Ollama")
        self.api_url = settings.get('ai_models.primary.api_url', 'http://localhost:11434')
        self.model = settings.get('ai_models.primary.model', 'llama2')
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        '''Check if Ollama is running'''
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.available = True
                self.logger.info("Ollama is available")
            else:
                self.logger.warning("Ollama is not responding")
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
            self.available = False
    
    async def generate(self, messages: List[Dict], system_prompt: str) -> Optional[str]:
        '''Generate response using Ollama'''
        if not self.available:
            return None
        
        try:
            # Convert messages to prompt
            prompt = self._build_prompt(messages, system_prompt)
            
            # Call Ollama API
            response = await asyncio.to_thread(
                requests.post,
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                self.logger.error(f"Ollama error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
            return None
    
    def _build_prompt(self, messages: List[Dict], system_prompt: str) -> str:
        '''Build prompt from messages'''
        prompt = f"System: {system_prompt}\\n\\n"
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            prompt += f"{role.capitalize()}: {content}\\n"
        
        prompt += "Assistant:"
        return prompt


class HuggingFaceProvider:
    '''Free Hugging Face models - No API key needed!'''
    
    def __init__(self):
        self.logger = Logger("HuggingFace")
        self.model_name = settings.get('ai_models.fallback.model', 'microsoft/DialoGPT-medium')
        self.tokenizer = None
        self.model = None
        self.available = False
        self._load_model()
    
    def _load_model(self):
        '''Load HuggingFace model'''
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            self.logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.available = True
            self.logger.info("HuggingFace model loaded successfully")
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
            
            # Encode input
            inputs = self.tokenizer.encode(user_message + self.tokenizer.eos_token, return_tensors='pt')
            
            # Generate response
            outputs = await asyncio.to_thread(
                self.model.generate,
                inputs,
                max_length=200,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_p=0.95,
                top_k=50
            )
            
            # Decode response
            response = self.tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
            return response.strip()
            
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