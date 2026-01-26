"""
FastAPI dependencies.

Reusable dependencies for authentication and authorization.
"""

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.core.security import (
    UserIdentity,
    create_local_bypass_user,
    get_user_from_request,
    verify_supabase_jwt,
)


def _extract_bearer_token(request: Request) -> str | None:
    """
    Extract bearer token from Authorization header.

    Returns token string if present and valid, None otherwise.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    if not auth_header.lower().startswith("bearer "):
        return None

    token = auth_header[7:].strip()
    return token or None


def _extract_dev_user_id(request: Request) -> str | None:
    """
    Extract dev user ID from X-Dev-User header (local bypass only).

    Returns user ID string if present, None otherwise.
    Only used when AUTH_BYPASS_LOCAL is enabled.
    """
    return request.headers.get("X-Dev-User", "").strip() or None


async def _resolve_user(request: Request, required: bool) -> UserIdentity | None:
    """
    Internal resolver for user authentication.

    DRY helper that handles both optional and required auth cases.

    Args:
        request: FastAPI Request object
        required: If True, raises UnauthorizedError when auth fails

    Returns:
        UserIdentity if authenticated, None if optional and not authenticated

    Raises:
        UnauthorizedError if required=True and authentication fails
    """
    settings = get_settings()

    # Cached on request.state
    user = get_user_from_request(request)
    if user:
        return user

    # Local bypass
    if settings.ENV == "local" and settings.AUTH_BYPASS_LOCAL:
        dev_user_id = _extract_dev_user_id(request)
        user = create_local_bypass_user(dev_user_id)
        request.state.user = user
        return user

    # Token auth
    token = _extract_bearer_token(request)
    if not token:
        if required:
            raise UnauthorizedError("Authentication required")
        return None

    try:
        user = verify_supabase_jwt(token)
        request.state.user = user
        return user
    except UnauthorizedError:
        if required:
            raise
        return None


async def get_optional_user(request: Request) -> UserIdentity | None:
    """
    Optional user dependency.

    Returns UserIdentity if authenticated, None if anonymous.
    Use this for endpoints that work for both authenticated and anonymous users.
    """
    return await _resolve_user(request, required=False)


async def require_user(request: Request) -> UserIdentity:
    """
    Required user dependency.

    Returns UserIdentity if authenticated, raises 401 if missing/invalid.
    Use this for endpoints that require authentication.
    """
    user = await _resolve_user(request, required=True)
    # Explicit check instead of assert (assert can be disabled with -O flag)
    if user is None:
        raise UnauthorizedError("Authentication required")
    return user


# Alias for consistency
get_current_user = require_user


# Usage in FastAPI endpoints:
#
# For optional auth:
#   user: UserIdentity | None = Depends(get_optional_user)
#
# For required auth:
#   user: UserIdentity = Depends(require_user)
