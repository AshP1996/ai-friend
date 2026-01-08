"""
Advanced multi-modal emotion detection with context awareness
Combines text sentiment, pitch analysis, conversation context, and intensity
"""
from typing import Dict, Any, List, Optional
import re
from textblob import TextBlob
from utils.logger import Logger

logger = Logger("AdvancedEmotionAnalyzer")

class AdvancedEmotionAnalyzer:
    """Advanced emotion detection with multi-modal fusion and context awareness"""
    
    def __init__(self):
        self.logger = logger
        
        # Expanded emotion patterns with intensity indicators
        self.emotion_patterns = {
            'joy': {
                'keywords': {'happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'perfect', 'fantastic', 'awesome', 'delighted', 'thrilled', 'ecstatic'},
                'intensifiers': {'so', 'very', 'really', 'extremely', 'incredibly'},
                'negators': {'not', 'never', 'no'}
            },
            'sadness': {
                'keywords': {'sad', 'depressed', 'unhappy', 'terrible', 'awful', 'crying', 'miserable', 'down', 'upset', 'disappointed', 'hurt'},
                'intensifiers': {'so', 'very', 'really', 'extremely'},
                'negators': {'not', 'never', 'no'}
            },
            'anger': {
                'keywords': {'angry', 'furious', 'mad', 'annoyed', 'frustrated', 'hate', 'rage', 'irritated'},
                'intensifiers': {'so', 'very', 'really', 'extremely', 'absolutely'},
                'negators': {'not', 'never', 'no'}
            },
            'fear': {
                'keywords': {'scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified', 'frightened', 'panic'},
                'intensifiers': {'so', 'very', 'really', 'extremely'},
                'negators': {'not', 'never', 'no'}
            },
            'excited': {
                'keywords': {'excited', 'thrilled', 'pumped', 'energized', 'cant wait', 'wow', 'yay', 'awesome', 'amazing'},
                'intensifiers': {'so', 'very', 'really', 'extremely', 'super'},
                'negators': {'not', 'never', 'no'}
            },
            'calm': {
                'keywords': {'calm', 'peaceful', 'relaxed', 'serene', 'chill', 'cool', 'fine', 'okay'},
                'intensifiers': {'so', 'very', 'really', 'quite'},
                'negators': {'not', 'never', 'no'}
            },
            'friendly': {
                'keywords': {'friendly', 'nice', 'kind', 'warm', 'welcoming', 'pleasant', 'good'},
                'intensifiers': {'so', 'very', 'really', 'quite'},
                'negators': {'not', 'never', 'no'}
            }
        }
        
        # Emotion transition patterns (context-aware)
        self.emotion_transitions = {
            'joy': ['excited', 'happy', 'friendly'],
            'sadness': ['calm', 'neutral'],
            'anger': ['calm', 'neutral'],
            'fear': ['calm', 'friendly'],
            'excited': ['happy', 'joy'],
            'neutral': ['friendly', 'calm']
        }
    
    async def analyze(self, text: str, context: Optional[Dict[str, Any]] = None, 
                     pitch_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Advanced multi-modal emotion analysis
        
        Args:
            text: Input text to analyze
            context: Conversation context (previous emotions, topics)
            pitch_data: Voice pitch analysis data
        
        Returns:
            Comprehensive emotion analysis with confidence scores
        """
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # 1. TEXT-BASED EMOTION DETECTION (enhanced)
        emotion_scores = {}
        intensity_multiplier = 1.0
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = len(words & patterns['keywords'])
            if keyword_matches > 0:
                score += keyword_matches * 0.3
            
            # Check for intensifiers before keywords
            for intensifier in patterns['intensifiers']:
                if intensifier in text_lower:
                    # Check if intensifier is near emotion keywords
                    intensifier_pos = text_lower.find(intensifier)
                    for keyword in patterns['keywords']:
                        keyword_pos = text_lower.find(keyword)
                        if keyword_pos != -1 and abs(intensifier_pos - keyword_pos) < 20:
                            intensity_multiplier = max(intensity_multiplier, 1.5)
                            score += 0.2
                            break
            
            # Check for negators (invert emotion)
            for negator in patterns['negators']:
                if negator in text_lower:
                    negator_pos = text_lower.find(negator)
                    for keyword in patterns['keywords']:
                        keyword_pos = text_lower.find(keyword)
                        if keyword_pos != -1 and abs(negator_pos - keyword_pos) < 10:
                            score *= 0.3  # Reduce emotion score
                            break
            
            if score > 0:
                emotion_scores[emotion] = score * intensity_multiplier
        
        # 2. SENTIMENT ANALYSIS (TextBlob)
        blob = TextBlob(text)
        sentiment = blob.sentiment
        sentiment_polarity = sentiment.polarity
        sentiment_subjectivity = sentiment.subjectivity
        
        # Map sentiment to emotions
        if sentiment_polarity > 0.4:
            emotion_scores['joy'] = emotion_scores.get('joy', 0) + sentiment_polarity * 0.5
        elif sentiment_polarity > 0.1:
            emotion_scores['friendly'] = emotion_scores.get('friendly', 0) + sentiment_polarity * 0.3
        elif sentiment_polarity < -0.4:
            emotion_scores['sadness'] = emotion_scores.get('sadness', 0) + abs(sentiment_polarity) * 0.5
        elif sentiment_polarity < -0.1:
            emotion_scores['anger'] = emotion_scores.get('anger', 0) + abs(sentiment_polarity) * 0.3
        
        # 3. INTENSITY DETECTION (punctuation, caps, repetition)
        intensity = self._detect_intensity(text)
        if intensity == 'very_high':
            for emotion in emotion_scores:
                emotion_scores[emotion] *= 1.5
        elif intensity == 'high':
            for emotion in emotion_scores:
                emotion_scores[emotion] *= 1.2
        
        # 4. PITCH-BASED EMOTION (if available)
        if pitch_data:
            pitch_emotion = self._pitch_to_emotion(pitch_data)
            if pitch_emotion:
                emotion_scores[pitch_emotion] = emotion_scores.get(pitch_emotion, 0) + 0.4
                self.logger.debug(f"Pitch emotion contribution: {pitch_emotion}")
        
        # 5. CONTEXT-AWARE ADJUSTMENT (conversation flow)
        if context:
            previous_emotion = context.get('previous_emotion')
            if previous_emotion and previous_emotion in self.emotion_transitions:
                # Boost emotions that are natural transitions
                for transition_emotion in self.emotion_transitions[previous_emotion]:
                    if transition_emotion in emotion_scores:
                        emotion_scores[transition_emotion] *= 1.1
        
        # 6. DETERMINE PRIMARY EMOTION
        if emotion_scores:
            primary_emotion, confidence = max(emotion_scores.items(), key=lambda x: x[1])
            # Normalize confidence to 0-1 range
            total_score = sum(emotion_scores.values())
            confidence = min(1.0, confidence / max(total_score, 1.0))
        else:
            # Fallback to sentiment-based
            if sentiment_polarity > 0.2:
                primary_emotion = 'friendly'
                confidence = 0.6
            elif sentiment_polarity < -0.2:
                primary_emotion = 'sadness'
                confidence = 0.6
            else:
                primary_emotion = 'neutral'
                confidence = 0.5
        
        # 7. EMOTION INTENSITY LEVEL
        intensity_level = self._calculate_intensity_level(emotion_scores, intensity, confidence)
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': round(confidence, 3),
            'all_emotions': {k: round(v, 3) for k, v in emotion_scores.items()},
            'sentiment_score': round(sentiment_polarity, 3),
            'subjectivity': round(sentiment_subjectivity, 3),
            'intensity': intensity,
            'intensity_level': intensity_level,
            'pitch_contribution': pitch_data.get('emotion_hint') if pitch_data else None,
            'context_aware': context is not None
        }
    
    def _detect_intensity(self, text: str) -> str:
        """Detect emotional intensity from text features"""
        intensity = 'low'
        
        # Exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count >= 3:
            intensity = 'very_high'
        elif exclamation_count >= 2:
            intensity = 'high'
        elif exclamation_count >= 1:
            intensity = 'medium'
        
        # All caps
        if text.isupper() and len(text) > 3:
            intensity = 'very_high' if intensity == 'very_high' else 'high'
        
        # Repeated letters (e.g., "sooo", "yesss")
        if re.search(r'([a-z])\1{2,}', text.lower()):
            intensity = 'high' if intensity != 'very_high' else 'very_high'
        
        # Question marks (uncertainty can indicate emotion)
        if text.count('?') >= 2:
            intensity = 'medium' if intensity == 'low' else intensity
        
        return intensity
    
    def _pitch_to_emotion(self, pitch_data: Dict[str, Any]) -> Optional[str]:
        """Convert pitch analysis to emotion"""
        emotion_hint = pitch_data.get('emotion_hint')
        pitch_hz = pitch_data.get('pitch_hz', 0)
        variation = pitch_data.get('pitch_variation', 0)
        
        if emotion_hint:
            # Map pitch hints to our emotion set
            mapping = {
                'excited': 'excited',
                'happy': 'joy',
                'sad': 'sadness',
                'emotional': 'excited',  # High variation = emotional
                'neutral': None
            }
            return mapping.get(emotion_hint)
        
        # Direct pitch mapping
        if pitch_hz > 200:
            return 'excited'
        elif pitch_hz > 160:
            return 'joy'
        elif pitch_hz < 120:
            return 'sadness'
        
        return None
    
    def _calculate_intensity_level(self, emotion_scores: Dict[str, float], 
                                   intensity: str, confidence: float) -> str:
        """Calculate overall emotional intensity level"""
        if not emotion_scores:
            return 'neutral'
        
        max_score = max(emotion_scores.values()) if emotion_scores else 0
        
        if intensity == 'very_high' or (max_score > 2.0 and confidence > 0.8):
            return 'very_high'
        elif intensity == 'high' or (max_score > 1.0 and confidence > 0.7):
            return 'high'
        elif max_score > 0.5 and confidence > 0.6:
            return 'medium'
        else:
            return 'low'
