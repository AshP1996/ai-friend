from typing import Dict, Any
from .base_agent import BaseAgent
from config.constants import EmotionType
import re

class EmotionAgent(BaseAgent):
    def __init__(self):
        super().__init__("emotion")
        self.emotion_keywords = {
            EmotionType.HAPPY: ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love'],
            EmotionType.SAD: ['sad', 'unhappy', 'depressed', 'terrible', 'awful', 'crying'],
            EmotionType.EXCITED: ['excited', 'thrilled', 'pumped', 'energized', 'cant wait'],
            EmotionType.CONFUSED: ['confused', 'dont understand', 'unclear', 'puzzled'],
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get('text', '').lower()

        emotion_scores = {}

        for emotion, keywords in self.emotion_keywords.items():
            score = sum(
                1 for kw in keywords
                if re.search(rf'\b{re.escape(kw)}\b', text)
            )
            if score:
                emotion_scores[emotion.value] = score

        if '!' in text:
            emotion_scores[EmotionType.EXCITED.value] = emotion_scores.get(EmotionType.EXCITED.value, 0) + 1

        detected = max(emotion_scores, key=emotion_scores.get) if emotion_scores else EmotionType.NEUTRAL.value

        total = sum(emotion_scores.values()) or 1

        return {
            'emotion': detected,
            'confidence': round(emotion_scores.get(detected, 0) / total, 2),
            'all_emotions': emotion_scores
        }