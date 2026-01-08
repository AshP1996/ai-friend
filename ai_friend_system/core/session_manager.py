"""
Multi-user session manager for isolated AI instances
"""

from typing import Dict
from datetime import datetime, timedelta
import asyncio
from .ai_friend import AIFriend
from utils.logger import Logger


class AIFriendSession:
    def __init__(self, user_id: str):
        self.user_id = str(user_id)
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
        return (datetime.now() - self.last_accessed) > timedelta(minutes=timeout_minutes)


class AIFriendSessions:
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, AIFriendSession] = {}
        self.session_timeout = session_timeout_minutes
        self.logger = Logger("SessionManager")

    async def get_or_create(self, user_id: str) -> AIFriendSession:
        user_id = str(user_id)

        if user_id not in self.sessions:
            self.logger.info(f"Creating new session for user: {user_id}")
            session = AIFriendSession(user_id)
            await session.initialize()
            self.sessions[user_id] = session
        else:
            self.sessions[user_id].last_accessed = datetime.now()

        return self.sessions[user_id]

    async def remove(self, user_id: str):
        user_id = str(user_id)
        if user_id in self.sessions:
            del self.sessions[user_id]
            self.logger.info(f"Removed session for user: {user_id}")

    async def cleanup_expired(self):
        expired_users = [
            uid for uid, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        for uid in expired_users:
            await self.remove(uid)

    async def start_cleanup_task(self):
        while True:
            await asyncio.sleep(300)
            await self.cleanup_expired()

    def get_active_sessions(self) -> int:
        return len(self.sessions)


# ✅ GLOBAL INSTANCE
sessions = AIFriendSessions()
