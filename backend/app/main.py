"""
ASASelfHosted.com Backend API

API-first architecture with consent-first design.
Backend enforces rules, not UI.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.errors import setup_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    
    Handles startup and shutdown events.
    Replaces deprecated @app.on_event("startup") pattern.
    """
    # Startup
    logger = logging.getLogger("asaselfhosted.startup")
    try:
        from app.workers.heartbeat_worker import process_heartbeat_jobs
        
        # Start heartbeat worker as background task (non-blocking)
        asyncio.create_task(process_heartbeat_jobs())
        logger.info("Heartbeat worker started as background task")
    except Exception as e:
        # Non-fatal - worker can be started separately if needed
        logger.warning(f"Failed to start heartbeat worker (non-fatal): {e}")
    
    yield  # App runs here
    
    # Shutdown (if needed in future)
    # Currently no cleanup needed, but this is where it would go


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns configured FastAPI app instance.
    """
    settings = get_settings()

    # Validate config early (prevent booting broken environments)
    # Enforces required config in staging/production and safety walls like auth bypass
    settings.validate_non_local()

    # Startup config banner
    logger = logging.getLogger("asaselfhosted.startup")
    
    auth_mode = "BYPASS" if (settings.ENV == "local" and settings.AUTH_BYPASS_LOCAL) else "REAL"
    cors_count = len(settings.cors_origins_list)
    cors_list = ", ".join(settings.cors_origins_list[:3]) + ("..." if cors_count > 3 else "")
    
    logger.info("=" * 60)
    logger.info("ASASelfHosted.com API Starting")
    logger.info(f"ENV: {settings.ENV}")
    logger.info(f"AUTH MODE: {auth_mode}")
    logger.info(f"DIRECTORY VIEW: {settings.DIRECTORY_VIEW_NAME}")
    logger.info(f"CORS ORIGINS: {cors_count} ({cors_list})")
    logger.info("=" * 60)

    # Initialize Sentry if DSN is provided and package is available
    # Moved here for deterministic startup and testability
    try:
        import sentry_sdk  # type: ignore
        from sentry_sdk.integrations.fastapi import FastApiIntegration  # type: ignore

        if settings.SENTRY_DSN:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[FastApiIntegration()],
                traces_sample_rate=1.0 if settings.ENV == "local" else 0.1,
                environment=settings.ENV,
            )
    except ImportError:
        # Sentry not installed, continue without it
        pass

    app = FastAPI(
        title="ASASelfHosted.com API",
        description="Public registry API for self-hosted Ark: Survival Ascended servers",
        version="0.1.0",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url="/redoc" if settings.ENV != "production" else None,
        lifespan=lifespan,  # Use lifespan handler instead of deprecated on_event
    )

    # CORS configuration
    cors_origins = settings.cors_origins_list

    # Dev fallback only (non-local validation ensures staging/prod is correct)
    if not cors_origins:
        cors_origins = ["http://localhost:3000", "http://localhost:5173"]

    # Starlette rejects "*" with allow_credentials=True; keep it out of non-local environments
    if "*" in cors_origins and settings.ENV in ("staging", "production"):
        raise ValueError("Cannot use '*' origin with allow_credentials=True in staging/production")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "X-Request-ID",
            "X-Dev-User",
        ],
    )

    # Add request ID middleware (must be before error handlers)
    from app.middleware.request_id import request_id_middleware

    app.middleware("http")(request_id_middleware)

    # Setup error handlers (after middleware so request_id is available)
    setup_error_handlers(app)

    # Include API routers
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


# Create app instance
app = create_app()
