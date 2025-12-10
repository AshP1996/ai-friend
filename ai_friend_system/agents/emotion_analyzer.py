"""
Advanced emotion detection with sentiment analysis
"""

from typing import Dict, Any
import re
from textblob import TextBlob

class AdvancedEmotionAnalyzer:
    def __init__(self):
        self.emotion_patterns = {
            'joy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'perfect'],
            'sadness': ['sad', 'depressed', 'unhappy', 'terrible', 'awful', 'crying', 'miserable'],
            'anger': ['angry', 'furious', 'mad', 'annoyed', 'frustrated', 'hate'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified'],
            'surprise': ['wow', 'amazing', 'unexpected', 'shocking', 'unbelievable'],
            'disgust': ['disgusting', 'gross', 'awful', 'terrible', 'nasty'],
            'trust': ['believe', 'trust', 'confident', 'sure', 'certain'],
        }
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        '''Advanced emotion analysis with sentiment scoring'''
        
        # Sentiment analysis
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Pattern matching
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in self.emotion_patterns.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                emotions[emotion] = score / len(keywords)
        
        # Determine primary emotion
        if emotions:
            primary_emotion = max(emotions.items(), key=lambda x: x[1])
        else:
            # Use sentiment to determine emotion
            if sentiment.polarity > 0.3:
                primary_emotion = ('joy', sentiment.polarity)
            elif sentiment.polarity < -0.3:
                primary_emotion = ('sadness', abs(sentiment.polarity))
            else:
                primary_emotion = ('neutral', 0.5)
        
        # Detect intensity
        intensity = 'low'
        if '!' in text or text.isupper():
            intensity = 'high'
        elif '!!' in text or '!!!' in text:
            intensity = 'very_high'
        
        return {
            'primary_emotion': primary_emotion[0],
            'confidence': primary_emotion[1],
            'all_emotions': emotions,
            'sentiment_score': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'intensity': intensity
        }