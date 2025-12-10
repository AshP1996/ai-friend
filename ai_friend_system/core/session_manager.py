# """
# Multi-user session manager for isolated AI instances
# Each user gets their own AI Friend with separate memory and context
# """

# from typing import Dict, Optional
# from datetime import datetime, timedelta
# import asyncio
# from .ai_friend import AIFriend
# from utils.logger import Logger
# import weakref
# from core.session_manager import sessions


# class AIFriendSession:
#     def __init__(self, user_id: str):
#         self.user_id = user_id
#         self.ai_friend = AIFriend()
#         self.created_at = datetime.now()
#         self.last_accessed = datetime.now()
#         self.is_initialized = False
    
#     async def initialize(self):
#         if not self.is_initialized:
#             await self.ai_friend.initialize()
#             await self.ai_friend.start_conversation(self.user_id)
#             self.is_initialized = True
    
#     async def chat(self, message: str):
#         self.last_accessed = datetime.now()
#         return await self.ai_friend.chat(message)
    
#     def is_expired(self, timeout_minutes: int = 30) -> bool:
#         elapsed = datetime.now() - self.last_accessed
#         return elapsed > timedelta(minutes=timeout_minutes)


# class AIFriendSessions:
#     '''Manages multiple concurrent user sessions'''
    
#     def __init__(self, session_timeout_minutes: int = 30):
#         self.sessions: Dict[str, AIFriendSession] = {}
#         self.session_timeout = session_timeout_minutes
#         self.logger = Logger("SessionManager")
#         self._cleanup_task = None
    
#     async def get_or_create(self, user_id: str) -> AIFriendSession:
#         '''Get existing session or create new one'''
#         if user_id not in self.sessions:
#             self.logger.info(f"Creating new session for user: {user_id}")
#             session = AIFriendSession(user_id)
#             await session.initialize()
#             self.sessions[user_id] = session
#         else:
#             self.sessions[user_id].last_accessed = datetime.now()
        
#         return self.sessions[user_id]
    
#     async def remove(self, user_id: str):
#         '''Manually remove a session'''
#         if user_id in self.sessions:
#             del self.sessions[user_id]
#             self.logger.info(f"Removed session for user: {user_id}")
    
#     async def cleanup_expired(self):
#         '''Remove expired sessions'''
#         expired = [
#             user_id for user_id, session in self.sessions.items()
#             if session.is_expired(self.session_timeout)
#         ]
        
#         for user_id in expired:
#             await self.remove(user_id)
#             self.logger.info(f"Cleaned up expired session: {user_id}")
    
#     async def start_cleanup_task(self):
#         '''Background task to cleanup expired sessions'''
#         while True:
#             await asyncio.sleep(300)  # Every 5 minutes
#             await self.cleanup_expired()
    
#     def get_active_sessions(self) -> int:
#         return len(self.sessions)
    
#     def get_session_info(self) -> Dict:
#         return {
#             'active_sessions': len(self.sessions),
#             'sessions': [
#                 {
#                     'user_id': user_id,
#                     'created_at': session.created_at.isoformat(),
#                     'last_accessed': session.last_accessed.isoformat()
#                 }
#                 for user_id, session in self.sessions.items()
#             ]
#         }

"""
Multi-user session manager for isolated AI instances
Each user gets their own AI Friend with separate memory and context
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio
from .ai_friend import AIFriend
from utils.logger import Logger


class AIFriendSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.ai_friend = AIFriend()
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.is_initialized = False
    
    async def initialize(self):
        if not self.is_initialized:
            await self.ai_friend.initialize()
            await self.ai_friend.start_conversation(self.user_id)
            self.is_initialized = True
    
    async def chat(self, message: str):
        self.last_accessed = datetime.now()
        return await self.ai_friend.chat(message)
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        elapsed = datetime.now() - self.last_accessed
        return elapsed > timedelta(minutes=timeout_minutes)


class AIFriendSessions:
    """Manages multiple concurrent user sessions"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, AIFriendSession] = {}
        self.session_timeout = session_timeout_minutes
        self.logger = Logger("SessionManager")
        self._cleanup_task = None
    
    async def get_or_create(self, user_id: str) -> AIFriendSession:
        """Get existing session or create new one"""
        if user_id not in self.sessions:
            self.logger.info(f"Creating new session for user: {user_id}")
            session = AIFriendSession(user_id)
            await session.initialize()
            self.sessions[user_id] = session
        else:
            self.sessions[user_id].last_accessed = datetime.now()
        
        return self.sessions[user_id]
    
    async def remove(self, user_id: str):
        """Manually remove a session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            self.logger.info(f"Removed session for user: {user_id}")
    
    async def cleanup_expired(self):
        """Remove expired sessions"""
        expired = [
            user_id for user_id, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        
        for user_id in expired:
            await self.remove(user_id)
            self.logger.info(f"Cleaned up expired session: {user_id}")
    
    async def start_cleanup_task(self):
        """Background task to cleanup expired sessions"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            await self.cleanup_expired()
    
    def get_active_sessions(self) -> int:
        return len(self.sessions)
    
    def get_session_info(self) -> Dict:
        return {
            "active_sessions": len(self.sessions),
            "sessions": [
                {
                    "user_id": user_id,
                    "created_at": session.created_at.isoformat(),
                    "last_accessed": session.last_accessed.isoformat()
                }
                for user_id, session in self.sessions.items()
            ]
        }


# 🔥 IMPORTANT: Create global instance (THIS is what FastAPI imports)
sessions = AIFriendSessions()
