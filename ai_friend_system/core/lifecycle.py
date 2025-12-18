from utils.logger import Logger
from core.config import config
from services.redis_client import connect_redis, close_redis

log = Logger("Lifecycle")

class SystemLifecycle:
    started = False

    @classmethod
    async def startup(cls, app=None):
        if cls.started:
            return

        log.info("🔍 Validating environment")
        config.validate()

        log.info("🔗 Connecting Redis")
        await connect_redis()

        if app:
            log.info("🧪 Running startup diagnostics")
            from core.startup_diagnostics import StartupDiagnostics
            diagnostics = StartupDiagnostics(app)
            report = await diagnostics.run()

            if not report.get("healthy", True):
                raise RuntimeError("Startup diagnostics failed")

            app.state.startup_report = report

        log.info("✅ System startup complete")
        cls.started = True

    @classmethod
    async def shutdown(cls):
        log.info("👋 System shutting down")
        await close_redis()
        cls.started = False
