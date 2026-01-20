"""
FastAPI dependencies.

Reusable dependencies for authentication and authorization.
"""

from fastapi import Depends, Request

from app.core.errors import UnauthorizedError
from app.core.security import UserIdentity, get_user_from_request, verify_supabase_jwt


async def get_optional_user(request: Request) -> UserIdentity | None:
    """
    Optional user dependency.

    Returns UserIdentity if authenticated, None if anonymous.
    Use this for endpoints that work for both authenticated and anonymous users.
    """
    # Check if user is already in request.state (from middleware)
    user = get_user_from_request(request)
    if user:
        return user

    # Try to verify token if Authorization header is present
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            user = await verify_supabase_jwt(request)
            # Attach to request.state for downstream use
            request.state.user = user
            return user
        except UnauthorizedError:
            # Invalid token, but endpoint allows anonymous
            return None

    return None


async def require_user(request: Request) -> UserIdentity:
    """
    Required user dependency.

    Returns UserIdentity if authenticated, raises 401 if missing/invalid.
    Use this for endpoints that require authentication.
    """
    # Check if user is already in request.state
    user = get_user_from_request(request)
    if user:
        return user

    # Try to verify token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise UnauthorizedError("Authentication required")

    user = await verify_supabase_jwt(request)
    # Attach to request.state for downstream use
    request.state.user = user
    return user


# Usage in FastAPI endpoints:
# 
# For optional auth:
#   user: UserIdentity | None = Depends(get_optional_user)
#
# For required auth:
#   user: UserIdentity = Depends(require_user)
