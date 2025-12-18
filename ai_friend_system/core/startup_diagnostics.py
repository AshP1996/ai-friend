from typing import Dict, Any, List
from fastapi import FastAPI
from utils.logger import Logger

logger = Logger("StartupDiagnostics")


class StartupDiagnostics:
    def __init__(self, app: FastAPI):
        self.app = app
        self.report: Dict[str, Any] = {
            "routes": [],
            "services": {},
            "status": "unknown"
        }

    async def run(self) -> Dict[str, Any]:
        logger.info("🔍 Running startup diagnostics...")

        await self._check_routes()
        await self._check_services()

        self.report["status"] = (
            "healthy"
            if all(v["ok"] for v in self.report["services"].values())
            else "degraded"
        )

        logger.info(f"✅ Startup diagnostics complete ({self.report['status']})")
        return self.report

    async def _check_routes(self):
        routes = []
        for route in self.app.router.routes:
            if hasattr(route, "methods"):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods)
                })

        self.report["routes"] = routes
        logger.info(f"📌 Registered routes: {len(routes)}")

    async def _check_services(self):
        self.report["services"] = {
            "database": await self._check_database(),
            "redis": await self._check_redis(),
            "session_manager": await self._check_sessions(),
            "ai_core": await self._check_ai_core(),
        }

    async def _check_database(self):
        try:
            from config import db_config
            async for session in db_config.get_session():
                await session.execute("SELECT 1")
            return {"ok": True}
        except Exception as e:
            logger.error(f"DB check failed: {e}")
            return {"ok": False, "error": str(e)}

    async def _check_redis(self):
        try:
            from fastapi_limiter import FastAPILimiter
            return {"ok": FastAPILimiter.redis is not None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _check_sessions(self):
        try:
            from core.session_manager import sessions
            sessions.get_active_sessions()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _check_ai_core(self):
        try:
            from core.ai_friend import AIFriend
            ai = AIFriend()
            await ai.initialize()
            return {"ok": True}
        except Exception as e:
            logger.error(f"AI core failed: {e}")
            return {"ok": False, "error": str(e)}
