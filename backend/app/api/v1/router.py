"""
API v1 router.

All v1 endpoints are registered here.
Routes are organized by domain, not by HTTP method.
"""

from fastapi import APIRouter

from app.api.v1 import (
    clusters,
    consent,
    heartbeat,
    servers,
    subscriptions,
    verification,
    webhooks,
)

router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include all domain routers
router.include_router(servers.router)
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
    """
    return {
        "version": "1.0.0",
        "status": "active",
    }


@router.get("/health")
async def api_v1_health():
    """
    API v1 health check endpoint.
    """
    return {"status": "ok", "api": "v1"}
