import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_path = self.base_dir / "config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    # Existing properties...
    @property
    def anthropic_api_key(self) -> str:
        return os.getenv('ANTHROPIC_API_KEY', '')
    
    @property
    def openai_api_key(self) -> str:
        return os.getenv('OPENAI_API_KEY', '')
    
    # NEW: Redis configuration
    @property
    def redis_url(self) -> str:
        return os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # NEW: Celery configuration
    @property
    def celery_broker_url(self) -> str:
        return os.getenv('CELERY_BROKER_URL', self.redis_url)
    
    @property
    def celery_result_backend(self) -> str:
        return os.getenv('CELERY_RESULT_BACKEND', self.redis_url)
    
    # NEW: JWT Secret
    @property
    def jwt_secret_key(self) -> str:
        return os.getenv('JWT_SECRET_KEY', 'change-this-secret-key-in-production')
    
    @property
    def jwt_algorithm(self) -> str:
        return 'HS256'
    
    @property
    def access_token_expire_minutes(self) -> int:
        return int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    # Existing properties continue...
    @property
    def database_path(self) -> Path:
        path = self.base_dir / self.config['database']['path']
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def primary_model(self) -> Dict[str, str]:
        return self.config['ai_models']['primary']
    
    @property
    def fallback_model(self) -> Dict[str, str]:
        return self.config['ai_models']['fallback']
    
    @property
    def memory_config(self) -> Dict[str, Any]:
        return self.config['memory_tiers']
    
    @property
    def voice_config(self) -> Dict[str, Any]:
        return self.config['voice']
    
    @property
    def performance_config(self) -> Dict[str, Any]:
        return self.config['performance']
    
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value