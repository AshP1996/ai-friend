from typing import Dict, Any, List
from .base_agent import BaseAgent

class ContextAgent(BaseAgent):
    def __init__(self):
        super().__init__("context")
        self.context_indicators = {
            'question': ['?', 'what', 'when', 'where', 'why', 'how', 'who'],
            'statement': ['.', 'is', 'are', 'was', 'were'],
            'command': ['please', 'can you', 'could you', 'tell me', 'show me'],
            'personal': ['i', 'me', 'my', 'mine', 'myself']
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get('text', '').lower()
        history = input_data.get('history', [])
        
        # Detect intent
        intent_scores = {}
        for intent, indicators in self.context_indicators.items():
            score = sum(1 for ind in indicators if ind in text)
            if score > 0:
                intent_scores[intent] = score
        
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'statement'
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Determine if personal info
        is_personal = 'personal' in intent_scores or any(word in text for word in ['my name', 'i am', 'i like', 'i love'])
        
        return {
            'intent': primary_intent,
            'entities': entities,
            'is_personal_info': is_personal,
            'requires_memory': is_personal or 'remember' in text,
            'conversation_depth': len(history)
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        # Simple entity extraction
        words = text.split()
        entities = [w for w in words if w[0].isupper() and len(w) > 2]
        return entities