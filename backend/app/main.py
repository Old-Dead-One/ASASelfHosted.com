"""
ASASelfHosted.com Backend API

API-first architecture with consent-first design.
Backend enforces rules, not UI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.errors import setup_error_handlers

# Initialize Sentry if DSN is provided and package is available
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

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


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns configured FastAPI app instance.
    """
    app = FastAPI(
        title="ASASelfHosted.com API",
        description="Public registry API for self-hosted Ark: Survival Ascended servers",
        version="0.1.0",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url="/redoc" if settings.ENV != "production" else None,
    )

    # CORS configuration
    # Frontend origin will be configured via environment variables
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Setup error handlers
    setup_error_handlers(app)

    # Optional: Add auth middleware for global JWT verification
    # Most endpoints use dependencies (require_user/optional_user) instead
    # Uncomment if you want global auth middleware:
    # from app.middleware.auth import auth_middleware
    # app.middleware("http")(auth_middleware)

    # Include API routers
    app.include_router(v1_router)

    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        No authentication required.
        """
        return {"status": "ok"}

    return app


# Create app instance
app = create_app()
