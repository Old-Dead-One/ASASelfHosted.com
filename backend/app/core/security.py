"""
Security utilities.

JWT verification, token parsing, and user identity extraction.
"""

from typing import Any

import jwt
from fastapi import HTTPException, Request, status

from app.core.config import settings
from app.core.errors import UnauthorizedError


class UserIdentity:
    """
    Minimal user identity object attached to request.state.

    Contains only essential auth information.
    Profile data should be fetched from DB with RLS if needed.
    """

    def __init__(self, user_id: str, email: str | None = None, claims: dict[str, Any] | None = None):
        self.user_id = user_id
        self.email = email
        self.claims = claims or {}
        self.role = self.claims.get("role", "authenticated")


async def verify_supabase_jwt(request: Request) -> UserIdentity:
    """
    Verify Supabase JWT token and extract user identity.

    Returns UserIdentity object with user_id, email, and claims.
    Raises UnauthorizedError if token is invalid or missing.

    This is authentication, not authorization.
    Authorization is handled by RLS policies and server-side checks.
    """
    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise UnauthorizedError("Authorization header missing")

    # Extract token (format: "Bearer <token>")
    try:
        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() != "bearer":
            raise UnauthorizedError("Invalid authorization scheme")
    except ValueError:
        raise UnauthorizedError("Invalid authorization header format")

    # Verify token with Supabase
    # Supabase JWTs are signed with the project's JWT secret
    # We need the anon key or service role key to verify
    try:
        # Decode without verification first to get the algorithm
        unverified = jwt.decode(token, options={"verify_signature": False})
        algorithm = unverified.get("alg", "HS256")

        # For Supabase, we verify using the anon key
        # In production, you'd use the JWT secret from Supabase settings
        # For now, we'll use a placeholder - this needs to be configured
        if not settings.SUPABASE_ANON_KEY:
            # In development, allow bypass if no key configured
            # TODO: Remove this in production
            if settings.ENV == "local":
                # Return a mock user for local dev
                return UserIdentity(
                    user_id=unverified.get("sub", "dev-user"),
                    email=unverified.get("email"),
                    claims=unverified,
                )
            raise UnauthorizedError("Supabase configuration missing")

        # Verify token
        # Note: Supabase uses HS256 with the JWT secret
        # The anon key is not the JWT secret, but we can verify using Supabase client
        # For now, we'll decode and validate structure
        # TODO: Implement proper Supabase JWT verification using supabase-py client
        decoded = jwt.decode(
            token,
            settings.SUPABASE_ANON_KEY,
            algorithms=[algorithm],
            options={"verify_signature": True},
        )

        # Extract user identity
        user_id = decoded.get("sub")
        if not user_id:
            raise UnauthorizedError("Token missing user ID")

        return UserIdentity(
            user_id=user_id,
            email=decoded.get("email"),
            claims=decoded,
        )

    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise UnauthorizedError(f"Token verification failed: {str(e)}")


def get_user_from_request(request: Request) -> UserIdentity | None:
    """
    Get user identity from request.state if available.

    Returns None if no user is attached (public request).
    """
    return getattr(request.state, "user", None)

