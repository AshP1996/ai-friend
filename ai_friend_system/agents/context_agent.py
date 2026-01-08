from typing import Dict, Any, List
from .base_agent import BaseAgent

class ContextAgent(BaseAgent):
    def __init__(self):
        super().__init__("context")
        # Pre-compiled sets for faster lookup
        self.question_words = {'what', 'when', 'where', 'why', 'how', 'who', 'which', 'whose'}
        self.command_phrases = {'please', 'can you', 'could you', 'tell me', 'show me', 'help me'}
        self.personal_words = {'i', 'me', 'my', 'mine', 'myself', 'i am', 'my name', 'i like', 'i love'}

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raw_text = input_data.get('text', '')
        text = raw_text.lower()
        words = set(text.split())
        history = input_data.get('history', [])

        intent_scores = {}
        
        # Fast checks using set operations
        if '?' in text or words & self.question_words:
            intent_scores['question'] = 2
        
        if words & self.command_phrases:
            intent_scores['command'] = 2
        
        if '.' in text or any(w in words for w in {'is', 'are', 'was', 'were'}):
            intent_scores['statement'] = 1
        
        if words & {'i', 'me', 'my', 'mine'}:
            intent_scores['personal'] = 1

        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'statement'
        entities = self._extract_entities(raw_text)
        is_personal = bool(words & self.personal_words) or any(phrase in text for phrase in {'i am', 'my name', 'i like', 'i love'})

        return {
            'intent': primary_intent,
            'entities': entities,
            'is_personal_info': is_personal,
            'requires_memory': is_personal or 'remember' in text,
            'conversation_depth': len(history)
        }

    def _extract_entities(self, text: str) -> List[str]:
        # Fast entity extraction - only check capitalized words
        return [word for word in text.split() if word and word[0].isupper() and len(word) > 2]    