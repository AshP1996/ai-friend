import re
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
        raw_text = input_data.get('text', '')
        text = raw_text.lower()
        history = input_data.get('history', [])

        intent_scores = {}
        for intent, indicators in self.context_indicators.items():
            score = sum(
                1 for ind in indicators
                if re.search(rf'\b{re.escape(ind)}\b', text)
            )
            if score:
                intent_scores[intent] = score

        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'statement'

        entities = self._extract_entities(raw_text)

        is_personal = bool(
            re.search(r'\b(i am|my name|i like|i love)\b', text)
        )

        return {
            'intent': primary_intent,
            'entities': entities,
            'is_personal_info': is_personal,
            'requires_memory': is_personal or 'remember' in text,
            'conversation_depth': len(history)
        }


    # def _extract_entities(self, text: str) -> List[str]:
    #     # Simple entity extraction
    #     words = text.split()
    #     entities = [w for w in words if w[0].isupper() and len(w) > 2]
    #     return entities
    def _extract_entities(self, text: str) -> List[str]:
        return re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', text)    