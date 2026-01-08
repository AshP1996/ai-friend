from typing import Dict, Any
from .base_agent import BaseAgent
from config.constants import EmotionType

class EmotionAgent(BaseAgent):
    def __init__(self):
        super().__init__("emotion")
        # Pre-compiled keyword sets for faster lookup
        self.emotion_keywords = {
            EmotionType.HAPPY: {'happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'awesome', 'fantastic'},
            EmotionType.SAD: {'sad', 'unhappy', 'depressed', 'terrible', 'awful', 'crying', 'upset', 'down'},
            EmotionType.EXCITED: {'excited', 'thrilled', 'pumped', 'energized', 'cant wait', 'wow', 'yay'},
            EmotionType.CONFUSED: {'confused', 'dont understand', 'unclear', 'puzzled', 'lost', 'huh'},
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get('text', '').lower()
        words = set(text.split())  # Convert to set for O(1) lookup

        emotion_scores = {}

        # Fast set intersection instead of regex
        for emotion, keywords in self.emotion_keywords.items():
            matches = len(words & keywords)  # Set intersection
            if matches:
                emotion_scores[emotion.value] = matches

        # Quick punctuation check
        if '!' in text:
            emotion_scores[EmotionType.EXCITED.value] = emotion_scores.get(EmotionType.EXCITED.value, 0) + 1

        detected = max(emotion_scores, key=emotion_scores.get) if emotion_scores else EmotionType.NEUTRAL.value
        total = sum(emotion_scores.values()) or 1

        return {
            'emotion': detected,
            'confidence': round(emotion_scores.get(detected, 0) / total, 2),
            'all_emotions': emotion_scores
        }