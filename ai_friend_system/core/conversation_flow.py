"""
Advanced conversation flow tracking and topic continuity
Maintains conversation context, tracks topics, and ensures personality consistency
"""
from typing import Dict, Any, List, Optional, Set
from collections import deque
from datetime import datetime
from utils.logger import Logger

logger = Logger("ConversationFlow")

class ConversationFlowTracker:
    """Tracks conversation flow, topics, and maintains personality consistency"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.topic_history = deque(maxlen=max_history)
        self.emotion_history = deque(maxlen=max_history)
        self.intent_history = deque(maxlen=max_history)
        self.current_topic: Optional[str] = None
        self.topic_continuity_score = 0.0
        self.logger = logger
    
    def track_message(self, text: str, emotion: str, intent: Optional[str] = None):
        """Track a new message in conversation flow"""
        # Extract topic keywords
        topic_keywords = self._extract_topic_keywords(text)
        
        # Update topic if significant change
        if topic_keywords:
            if self.current_topic:
                # Check topic continuity
                overlap = len(set(topic_keywords) & set(self.current_topic.split()))
                if overlap < 2:  # Topic shift
                    self.topic_continuity_score = 0.3
                    self.current_topic = ' '.join(topic_keywords[:3])
                else:
                    self.topic_continuity_score = min(1.0, overlap / len(topic_keywords))
            else:
                self.current_topic = ' '.join(topic_keywords[:3])
                self.topic_continuity_score = 1.0
        
        # Track history
        self.topic_history.append({
            'keywords': topic_keywords,
            'timestamp': datetime.now()
        })
        self.emotion_history.append({
            'emotion': emotion,
            'timestamp': datetime.now()
        })
        if intent:
            self.intent_history.append({
                'intent': intent,
                'timestamp': datetime.now()
            })
    
    def _extract_topic_keywords(self, text: str) -> List[str]:
        """Extract key topic words from text"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract meaningful words (nouns, verbs, adjectives)
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Return top 5 most frequent or unique
        return keywords[:5]
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context for response generation"""
        recent_emotions = [e['emotion'] for e in list(self.emotion_history)[-3:]]
        emotion_trend = self._calculate_emotion_trend(recent_emotions)
        
        return {
            'current_topic': self.current_topic,
            'topic_continuity': round(self.topic_continuity_score, 2),
            'recent_emotions': recent_emotions,
            'emotion_trend': emotion_trend,
            'conversation_length': len(self.topic_history),
            'needs_topic_continuation': self.topic_continuity_score > 0.5
        }
    
    def _calculate_emotion_trend(self, emotions: List[str]) -> str:
        """Calculate emotion trend over recent messages"""
        if not emotions:
            return 'stable'
        
        # Count emotion types
        emotion_counts = {}
        for e in emotions:
            emotion_counts[e] = emotion_counts.get(e, 0) + 1
        
        # Determine trend
        if len(set(emotions)) == 1:
            return 'stable'
        elif any(e in ['happy', 'excited', 'joy'] for e in emotions[-2:]):
            return 'positive'
        elif any(e in ['sad', 'anger'] for e in emotions[-2:]):
            return 'negative'
        else:
            return 'neutral'
    
    def should_continue_topic(self) -> bool:
        """Determine if current topic should be continued"""
        return self.topic_continuity_score > 0.5 and self.current_topic is not None
    
    def get_suggested_response_style(self) -> Dict[str, Any]:
        """Get suggested response style based on conversation flow"""
        context = self.get_conversation_context()
        
        style = {
            'tone': 'friendly',
            'length': 'medium',  # short, medium, long
            'should_reference_topic': context['needs_topic_continuation'],
            'emotion_match': True
        }
        
        # Adjust based on emotion trend
        if context['emotion_trend'] == 'positive':
            style['tone'] = 'enthusiastic'
            style['length'] = 'medium'
        elif context['emotion_trend'] == 'negative':
            style['tone'] = 'supportive'
            style['length'] = 'long'  # More detailed, caring responses
        
        # Adjust based on topic continuity
        if context['needs_topic_continuation']:
            style['should_reference_topic'] = True
            style['length'] = 'medium'
        
        return style
