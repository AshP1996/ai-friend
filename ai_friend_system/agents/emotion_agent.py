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
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                emotion_scores[emotion.value] = score
        
        # Detect exclamation marks and caps
        if '!' in text or text.isupper():
            emotion_scores[EmotionType.EXCITED.value] = emotion_scores.get(EmotionType.EXCITED.value, 0) + 1
        
        if '?' in text and len(text.split()) < 10:
            emotion_scores[EmotionType.CONFUSED.value] = emotion_scores.get(EmotionType.CONFUSED.value, 0) + 0.5
        
        detected_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else EmotionType.NEUTRAL.value
        
        return {
            'emotion': detected_emotion,
            'confidence': emotion_scores.get(detected_emotion, 0) / 10,
            'all_emotions': emotion_scores
        }