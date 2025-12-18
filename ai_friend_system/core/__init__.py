"""
Core package exports for AI Friend system
Keeps public interfaces clean and avoids circular imports
"""

# ---- Core AI Components ----
from .ai_friend import AIFriend
from .nlp_engine import NLPEngine
from .response_generator import ResponseGenerator
from .message_processor import MessageProcessor

# ---- Session Management ----
from .session_manager import AIFriendSessions

# ---- System & Lifecycle (NEW) ----
from .lifecycle import SystemLifecycle
from .config import config

__all__ = [
    # AI
    "AIFriend",
    "NLPEngine",
    "ResponseGenerator",
    "MessageProcessor",

    # Sessions
    "AIFriendSessions",

    # System
    "SystemLifecycle",
    "config",
]
