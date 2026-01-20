"""
Authentication middleware.

Handles Supabase Auth token verification.
Extracts user information from JWT tokens and attaches to request.state.

Note: This middleware is optional. Most endpoints use dependencies (require_user/optional_user)
for more granular control. This middleware can be used for global auth if needed.
"""

from fastapi import Request

from app.core.security import UserIdentity, verify_supabase_jwt


async def auth_middleware(request: Request, call_next):
    """
    Optional authentication middleware.

    Verifies JWT token if Authorization header is present
    and attaches UserIdentity to request.state.

    This is optional - most endpoints use dependencies instead.
    """
    # Only process if Authorization header is present
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            user = await verify_supabase_jwt(request)
            request.state.user = user
        except Exception:
            # Invalid token, but don't fail here
            # Let individual endpoints handle auth requirements
            pass

    response = await call_next(request)
    return response
