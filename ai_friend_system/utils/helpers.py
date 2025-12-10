from typing import Dict, Any, List
import json
from datetime import datetime

class Helpers:
    @staticmethod
    def format_timestamp(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        try:
            return json.loads(json_str)
        except:
            return default
    
    @staticmethod
    def safe_json_dumps(obj: Any) -> str:
        try:
            return json.dumps(obj)
        except:
            return "{}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)