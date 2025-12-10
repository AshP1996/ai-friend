import re
from typing import Optional

class Validators:
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        if not user_id or len(user_id) < 3 or len(user_id) > 100:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', user_id))
    
    @staticmethod
    def validate_message(message: str) -> bool:
        if not message or len(message.strip()) == 0:
            return False
        if len(message) > 5000:
            return False
        return True
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>{}]', '', text)
        return sanitized.strip()