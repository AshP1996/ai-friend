# """
# Main FastAPI app with all advanced features
# """
# import datetime
# from core.startup_diagnostics import StartupDiagnostics
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter
# import redis.asyncio as redis
# from .middleware import timing_middleware, error_handler_middleware
# from .routes import chat, memory, voice, profile, agents, auth, analytics, persona, avatar
# from utils.logger import Logger

# app = FastAPI(
#     title="AI Friend - Advanced API",
#     description="Production-ready AI companion with advanced features",
#     version="2.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# logger = Logger("API")

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Security
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# # Custom middleware
# app.middleware("http")(timing_middleware)
# app.middleware("http")(error_handler_middleware)

# # Include all routers
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
# app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
# app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
# app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
# app.include_router(persona.router, prefix="/api/persona", tags=["Persona"])
# app.include_router(avatar.router, prefix="/api/avatar", tags=["Avatar"])

# @app.on_event("startup")
# async def startup_event():
#     logger.info("🚀 AI Friend API starting...")

#     # ---- Redis ----
#     try:
#         redis_client = redis.from_url(
#             "redis://localhost:6379",
#             encoding="utf-8",
#             decode_responses=True
#         )
#         await FastAPILimiter.init(redis_client)
#         logger.info("✅ Redis rate limiter initialized")
#     except Exception as e:
#         logger.warning(f"⚠️ Redis not available: {e}")

#     # ---- Session cleanup ----
#     from core.session_manager import sessions
#     import asyncio
#     asyncio.create_task(sessions.start_cleanup_task())

#     # ---- STARTUP DIAGNOSTICS ----
#     diagnostics = StartupDiagnostics(app)
#     app.state.startup_report = await diagnostics.run()

#     logger.info("✅ AI Friend API ready!")


# @app.on_event("shutdown")
# async def shutdown_event():
#     logger.info("👋 AI Friend API shutting down...")

# @app.get("/")
# async def root():
#     return {
#         "name": "AI Friend API",
#         "version": "2.0.0",
#         "status": "running",
#         "features": [
#             "Multi-user sessions",
#             "JWT authentication",
#             "Semantic memory",
#             "Emotion analysis",
#             "Voice processing",
#             "Real-time streaming",
#             "Analytics dashboard",
#             "3D avatar control",
#             "Background tasks",
#             "Rate limiting"
#         ],
#         "docs": "/docs"
#     }

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat()
#     }

# @app.get("/stats")
# async def system_stats():
#     from core.session_manager import sessions
#     return {
#         "active_sessions": sessions.get_active_sessions(),
#         "session_info": sessions.get_session_info()
#     }


"""
Main FastAPI app with all advanced features
"""
from datetime import datetime
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_limiter import FastAPILimiter

from core.lifecycle import SystemLifecycle
from services.redis_client import redis_client
from core.startup_diagnostics import StartupDiagnostics
from utils.logger import Logger

from .middleware import timing_middleware, error_handler_middleware
from .routes import (
    chat,
    memory,
    voice,
    profile,
    agents,
    auth,
    analytics,
    persona,
    avatar,
)

# ------------------------------------------------------------------
# APP INIT
# ------------------------------------------------------------------

app = FastAPI(
    title="AI Friend - Advanced API",
    description="Production-ready AI companion with advanced features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger = Logger("API")

# ------------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------------

# CORS (⚠️ restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts (⚠️ restrict in production)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

# Custom middleware
app.middleware("http")(timing_middleware)
app.middleware("http")(error_handler_middleware)

# ------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(persona.router, prefix="/api/persona", tags=["Persona"])
app.include_router(avatar.router, prefix="/api/avatar", tags=["Avatar"])

# ------------------------------------------------------------------
# STARTUP
# ------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Friend API starting...")

    # ---- SYSTEM LIFECYCLE (ENV + REDIS + DIAGNOSTICS) ----
    await SystemLifecycle.startup(app)

    # ---- RATE LIMITER ----
    try:
        await FastAPILimiter.init(redis_client)
        logger.info("✅ Redis rate limiter initialized")
    except Exception as e:
        logger.warning(f"⚠️ Rate limiter disabled: {e}")

    # ---- SESSION CLEANUP TASK ----
    from core.session_manager import sessions
    asyncio.create_task(sessions.start_cleanup_task())

    logger.info("✅ AI Friend API ready!")

# ------------------------------------------------------------------
# SHUTDOWN
# ------------------------------------------------------------------

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 AI Friend API shutting down...")
    await SystemLifecycle.shutdown()

# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "name": "AI Friend API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Multi-user sessions",
            "JWT authentication",
            "Semantic memory",
            "Emotion analysis",
            "Voice processing",
            "Real-time streaming",
            "Analytics dashboard",
            "3D avatar control",
            "Background tasks",
            "Rate limiting",
        ],
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    report = getattr(app.state, "startup_report", {})
    return {
        "status": "healthy",
        "redis": bool(report),
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/stats")
async def system_stats():
    from core.session_manager import sessions
    return {
        "active_sessions": sessions.get_active_sessions(),
    }
