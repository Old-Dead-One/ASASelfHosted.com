"""
Security utilities.

JWT verification, token parsing, and user identity extraction.
"""

import time
from typing import TYPE_CHECKING, Any

import httpx
import jwt
from jwt import InvalidTokenError
from jwt.algorithms import RSAAlgorithm

from app.core.config import get_settings
from app.core.errors import UnauthorizedError

if TYPE_CHECKING:
    from fastapi import Request

# JWKS cache (in-memory, simple TTL-based)
_jwks_cache: dict[str, tuple[dict, float]] = {}
_jwks_cache_ttl = 3600  # 1 hour cache


class UserIdentity:
    """
    Minimal user identity object attached to request.state.

    Contains only essential auth information.
    Profile data should be fetched from DB with RLS if needed.

    Note: user_id is effectively the 'sub' claim from JWT.
    This is the single consistent backend auth contract.
    """

    def __init__(
        self,
        user_id: str,
        email: str | None = None,
        claims: dict[str, Any] | None = None,
    ):
        self.user_id = user_id  # This is the 'sub' claim from JWT
        self.email = email
        self.claims = claims or {}
        self.role = self.claims.get("role", "authenticated")

    @property
    def sub(self) -> str:
        """
        Convenience property: sub is the same as user_id.

        JWT 'sub' claim maps to user_id in our model.
        """
        return self.user_id


def _create_local_dev_user(dev_user_id: str | None = None) -> UserIdentity:
    """
    Create a stable fake user for local development bypass mode.

    Args:
        dev_user_id: Optional custom user ID (from X-Dev-User header)
                    Will be prefixed with "dev:" to make it obviously synthetic.

    Returns:
        UserIdentity with stable fake user data
    """
    # Normalize dev user ID: prefix with "dev:" to make it obviously synthetic
    # This prevents accidental abuse (e.g., X-Dev-User: admin won't become "admin")
    if dev_user_id:
        user_id = f"dev:{dev_user_id}"
    else:
        user_id = "dev:local-dev"

    return UserIdentity(
        user_id=user_id,
        email=f"{user_id}@local.dev",
        claims={
            "sub": user_id,
            "role": "authenticated",
            "email": f"{user_id}@local.dev",
        },
    )


def create_local_bypass_user(dev_user_id: str | None = None) -> UserIdentity:
    """
    Create a local bypass user (explicit helper for bypass mode).

    This should only be called when AUTH_BYPASS_LOCAL is enabled.
    Use this instead of calling verify_supabase_jwt() with a fake token.

    Args:
        dev_user_id: Optional custom user ID (from X-Dev-User header)

    Returns:
        UserIdentity with stable fake user data

    Raises:
        UnauthorizedError if bypass is not enabled
    """
    settings = get_settings()
    if settings.ENV != "local" or not settings.AUTH_BYPASS_LOCAL:
        raise UnauthorizedError(
            "Local bypass user is only available in local bypass mode"
        )
    return _create_local_dev_user(dev_user_id)


def _fetch_jwks(jwks_url: str) -> dict:
    """
    Fetch JWKS from Supabase endpoint.

    Args:
        jwks_url: JWKS endpoint URL

    Returns:
        JWKS dictionary with keys

    Raises:
        UnauthorizedError if fetch fails or response is invalid

    Note: Currently synchronous (httpx.get). Under load, this blocks the event loop
    when JWKS cache expires. Consider migrating to httpx.AsyncClient in Sprint 2.
    """
    try:
        response = httpx.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        jwks = response.json()

        # Validate JWKS response shape
        if not isinstance(jwks, dict) or "keys" not in jwks:
            raise UnauthorizedError("Invalid JWKS response format")

        return jwks
    except httpx.RequestError as e:
        raise UnauthorizedError(f"Failed to fetch JWKS: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise UnauthorizedError(f"JWKS endpoint returned {e.response.status_code}")
    except Exception as e:
        raise UnauthorizedError(f"Failed to parse JWKS: {str(e)}")


def _get_jwks_keys(jwks_url: str) -> dict:
    """
    Get JWKS keys with caching and stale-if-error fallback.

    Args:
        jwks_url: JWKS endpoint URL

    Returns:
        JWKS dictionary with keys

    Uses stale-if-error: if refresh fails but cached keys exist, return stale cache.
    This keeps auth working during JWKS endpoint hiccups.
    """
    now = time.time()

    # Check cache
    if jwks_url in _jwks_cache:
        keys, cached_at = _jwks_cache[jwks_url]
        if now - cached_at < _jwks_cache_ttl:
            return keys

        # TTL expired: try refresh, but fall back to stale cache on failure
        try:
            keys = _fetch_jwks(jwks_url)
            _jwks_cache[jwks_url] = (keys, now)
            return keys
        except UnauthorizedError:
            # Return stale cache if refresh fails (keeps API alive during JWKS blips)
            return keys

    # No cache: fetch and cache
    keys = _fetch_jwks(jwks_url)
    _jwks_cache[jwks_url] = (keys, now)
    return keys


def _get_public_key_from_jwks(jwks: dict, kid: str) -> Any:
    """
    Get public key from JWKS by key ID.

    Args:
        jwks: JWKS dictionary
        kid: Key ID from JWT header

    Returns:
        Public key for verification

    Raises:
        UnauthorizedError if key not found
    """
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return RSAAlgorithm.from_jwk(key)

    raise UnauthorizedError(f"JWK with kid '{kid}' not found in JWKS")


def verify_supabase_jwt(token: str) -> UserIdentity:
    """
    Verify Supabase JWT token and extract user identity.

    Args:
        token: JWT token string (without "Bearer " prefix)

    Returns:
        UserIdentity object with user_id (sub), email, and claims.

    Raises:
        UnauthorizedError if token is invalid or missing.

    This is authentication, not authorization.
    Authorization is handled by RLS policies and server-side checks.

    Uses JWKS (RS256) for signature verification.
    Note: Local bypass should use create_local_bypass_user() instead.
    """
    settings = get_settings()

    if not token:
        raise UnauthorizedError("Missing bearer token")

    # JWKS verification (real auth path)
    # In local mode without bypass, fail gracefully if JWKS not configured
    if not settings.SUPABASE_JWKS_URL:
        if settings.ENV == "local":
            raise UnauthorizedError(
                "JWKS URL not configured (set SUPABASE_JWKS_URL or enable AUTH_BYPASS_LOCAL)"
            )
        raise UnauthorizedError("JWKS URL not configured")

    try:
        # Decode header to get key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise UnauthorizedError("Token missing key ID (kid)")

        # Get JWKS and find the public key
        jwks = _get_jwks_keys(settings.SUPABASE_JWKS_URL)
        public_key = _get_public_key_from_jwks(jwks, kid)

        # Verify token signature and claims
        # Let PyJWT enforce issuer/audience (consistent, less drift)
        decode_kwargs: dict[str, Any] = {
            "key": public_key,
            "algorithms": ["RS256"],
            "options": {"require": ["exp", "sub"]},
        }

        # Let PyJWT enforce issuer/audience (consistent, less drift)
        if settings.SUPABASE_JWT_ISSUER:
            decode_kwargs["issuer"] = settings.SUPABASE_JWT_ISSUER

        if settings.SUPABASE_JWT_AUDIENCE:
            decode_kwargs["audience"] = settings.SUPABASE_JWT_AUDIENCE

        decoded = jwt.decode(token, **decode_kwargs)

        # Extract user identity (sub is the user ID)
        user_id = decoded.get("sub")
        if not user_id:
            raise UnauthorizedError("Token missing user ID (sub)")

        return UserIdentity(
            user_id=user_id,
            email=decoded.get("email"),
            claims=decoded,
        )

    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except InvalidTokenError as e:
        # Safe message; doesn't leak token contents
        raise UnauthorizedError(f"Invalid token: {str(e)}")
    except Exception as e:
        # In local/dev, make debugging possible
        if settings.ENV in ("local", "development"):
            raise UnauthorizedError(f"Token verification failed: {str(e)}")
        raise UnauthorizedError("Token verification failed")


def get_user_from_request(request: "Request") -> UserIdentity | None:
    """
    Get user identity from request.state if available.

    Args:
        request: FastAPI Request object

    Returns:
        UserIdentity if available, None if no user is attached (public request).
    """
    return getattr(request.state, "user", None)
