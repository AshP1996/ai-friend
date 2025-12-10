from typing import Dict, Any, List
from utils.logger import Logger
import re

class NLPEngine:
    def __init__(self):
        self.logger = Logger("NLPEngine")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        analysis = {
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'has_question': '?' in text,
            'has_exclamation': '!' in text,
            'capitalized_words': len([w for w in text.split() if w[0].isupper()]),
            'is_short': len(text.split()) < 5,
            'is_long': len(text.split()) > 50
        }
        
        return analysis
    
    def extract_key_phrases(self, text: str) -> List[str]:
        # Simple key phrase extraction
        words = text.lower().split()
        phrases = []
        
        # Extract noun phrases (simplified)
        for i in range(len(words) - 1):
            if len(words[i]) > 4:
                phrases.append(words[i])
        
        return phrases[:5]
    
    def clean_text(self, text: str) -> str:
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.!?,\'-]', '', text)
        return text.strip()