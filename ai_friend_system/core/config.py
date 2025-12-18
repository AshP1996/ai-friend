import os
from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     DEBUG = os.getenv("DEBUG", "false").lower() == "true"
#     LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

#     REDIS_URL = os.getenv("REDIS_URL")

#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

#     @classmethod
#     def validate(cls):
#         if not cls.REDIS_URL:
#             raise RuntimeError("REDIS_URL missing in .env")

#         if not cls.JWT_SECRET_KEY:
#             raise RuntimeError("JWT_SECRET_KEY missing")

# config = Config()

class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    REDIS_URL = os.getenv("REDIS_URL")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # ✅ ADD THIS
    AI_MODELS = {
        "primary": {
            "provider": "ollama",
            "api_url": os.getenv("OLLAMA_API_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "phi:latest"),
        },
        "fallback": {
            "provider": "huggingface",
            "model": "microsoft/DialoGPT-medium",
        },
        "cloud": {
            "openai": {
                "model": "gpt-3.5-turbo",
            },
            "anthropic": {
                "model": "claude-sonnet-4-20250514",
            },
        },
    }

    @classmethod
    def validate(cls):
        if not cls.REDIS_URL:
            raise RuntimeError("REDIS_URL missing in .env")
        if not cls.JWT_SECRET_KEY:
            raise RuntimeError("JWT_SECRET_KEY missing")

config = Config()