"""
Authentication middleware.

Handles Supabase Auth token verification.
Extracts user information from JWT tokens and attaches to request.state.

Note: This middleware is optional. Most endpoints use dependencies (require_user/optional_user)
for more granular control. This middleware can be used for global auth if needed.
"""

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.core.security import verify_supabase_jwt


async def auth_middleware(request: Request, call_next):
    """
    Optional authentication middleware.

    Verifies JWT token if Authorization header is present
    and attaches UserIdentity to request.state.

    This is optional - most endpoints use dependencies instead.
    Sets request.state.user = None initially, then sets it if token is valid.
    """
    # Initialize user state
    request.state.user = None

    settings = get_settings()
    
    # Local bypass: set fake user if enabled
    if settings.ENV == "local" and settings.AUTH_BYPASS_LOCAL:
        dev_user_id = request.headers.get("X-Dev-User", "").strip() or None
        request.state.user = verify_supabase_jwt("bypass-token", dev_user_id=dev_user_id)
        return await call_next(request)

    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        # Extract token (slice after "bearer " - 7 characters)
        token = auth_header[7:].strip()
        if token:
            try:
                # Verify token and set user
                request.state.user = verify_supabase_jwt(token)
            except UnauthorizedError:
                # Invalid token - don't fail, individual endpoints will handle auth requirements
                pass

    response = await call_next(request)
    return response
