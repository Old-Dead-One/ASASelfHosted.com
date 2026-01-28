"""
API v1 router.

All v1 endpoints are registered here.
Routes are organized by domain, not by HTTP method.

This router has no prefix - it's mounted at settings.API_V1_PREFIX in main.py.
Domain routers (servers, clusters, etc.) define their own prefixes and tags.
"""

from fastapi import APIRouter

from app.api.v1 import (
    clusters,
    consent,
    directory,
    favorites,
    heartbeat,
    servers,
    subscriptions,
    verification,
    webhooks,
)
from app.core.config import get_settings

router = APIRouter()

# Include all domain routers
# Directory router (read-only, public)
router.include_router(directory.router)
# Server router (CRUD, owner-managed)
router.include_router(servers.router)
# Favorites router (nested under servers)
router.include_router(favorites.router)
router.include_router(clusters.router)
router.include_router(verification.router)
router.include_router(heartbeat.router)
router.include_router(consent.router)
router.include_router(subscriptions.router)
router.include_router(webhooks.router)


@router.get("/")
async def api_v1_info():
    """
    API v1 information endpoint.

    Returns API version, app version, and environment.
    """
    settings = get_settings()
    return {
        "api_version": "v1",
        "app_version": "0.1.0",  # Matches FastAPI app version in main.py
        "environment": settings.ENV,
    }


@router.get("/health")
async def api_v1_health():
    """
    API v1 health check endpoint.
    """
    return {"status": "ok", "api": "v1"}
