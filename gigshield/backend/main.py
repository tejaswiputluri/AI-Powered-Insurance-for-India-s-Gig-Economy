"""
GigShield Backend — FastAPI Application Entry Point.
Wires together all routers, middleware, database, cache, and scheduler.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uuid as uuid_lib

from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("gigshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown."""
    logger.info("⚡ GigShield starting up...")
    logger.info(f"   DEMO_MODE: {settings.DEMO_MODE}")
    logger.info(f"   APP_ENV: {settings.APP_ENV}")

    # 1. Initialize database
    from backend.db.database import init_db, close_db
    await init_db()
    logger.info("✅ Database initialized")

    # 2. Seed demo data (if DEMO_MODE)
    if settings.DEMO_MODE:
        from backend.db.database import async_session_factory
        from backend.db.seed import seed_demo_data
        async with async_session_factory() as session:
            await seed_demo_data(session)

    # 3. Start scheduler
    from backend.scheduler.jobs import setup_scheduler
    setup_scheduler()
    logger.info("✅ Scheduler started")

    logger.info("⚡ GigShield is ready!")

    yield  # App is running

    # Shutdown
    logger.info("🛑 GigShield shutting down...")
    from backend.scheduler.jobs import scheduler
    scheduler.shutdown(wait=False)
    from backend.cache.redis_client import close_redis
    await close_redis()
    await close_db()
    logger.info("🛑 Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="GigShield API",
    description=(
        "AI-Powered Parametric Income Insurance for India's Gig Workers. "
        "Guidewire DEVTrails 2026 — Unicorn Chase."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Register API Routers ───────────────────────────────────────────

from backend.api.routers import auth, riders, policies, claims, triggers, insurer, demo

app.include_router(auth.router, prefix="/api/v1")
app.include_router(riders.router, prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1")
app.include_router(claims.router, prefix="/api/v1")
app.include_router(triggers.router, prefix="/api/v1")
app.include_router(insurer.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")


# ─── Standardized Error Handling (DEV-12 / Spec §5) ─────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return spec-compliant error format."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again.",
            },
        },
    )


from fastapi.exceptions import HTTPException as FastAPIHTTPException

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """
    Wrap HTTPException responses in the spec-mandated format:
    {"data": null, "error": {"code": "...", "message": "..."}}
    """
    detail = exc.detail
    if isinstance(detail, dict):
        error_body = {
            "code": detail.get("code", "ERROR"),
            "message": detail.get("message", str(detail)),
        }
    else:
        error_body = {"code": "ERROR", "message": str(detail)}

    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": error_body},
    )


# ─── Request ID Middleware ───────────────────────────────────────────────

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds a unique X-Request-ID header to every response for tracing."""
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid_lib.uuid4())[:8]
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)


# ─── Root and Health Endpoints ───────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "GigShield API",
        "version": "1.0.0",
        "tagline": "AI-Powered Parametric Income Insurance for India's Gig Workers",
        "demo_mode": settings.DEMO_MODE,
        "docs": "/api/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "demo_mode": settings.DEMO_MODE,
        "version": "1.0.0",
    }


@app.get("/api/v1/status")
async def api_status():
    """API status with service health."""
    services = {
        "database": "connected",
        "redis": "connected",
        "ml_premium": "unknown",
        "ml_forecast": "unknown",
        "ml_cnn": "unknown",
    }

    # Quick health checks
    try:
        from backend.cache.redis_client import get_redis
        redis = await get_redis()
        await redis.ping()
        services["redis"] = "healthy"
    except Exception:
        services["redis"] = "unhealthy"

    return {
        "data": {
            "status": "operational",
            "demo_mode": settings.DEMO_MODE,
            "services": services,
        },
        "error": None,
    }
