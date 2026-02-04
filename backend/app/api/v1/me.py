"""
Me / profile endpoints.

Handles current user profile, terms acceptance (legal audit), consent state (Sprint 8),
and per-user limits (Sprint 9).
"""

from typing import Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.deps import extract_bearer_token, require_user
from app.core.limits import get_effective_limits
from app.core.security import UserIdentity
from app.core.supabase import get_supabase_admin, get_rls_client
from app.db.providers import get_servers_repo

router = APIRouter(prefix="/me", tags=["me"])


class FavoriteServerItem(BaseModel):
    """Minimal server info for favorites list (dashboard)."""

    id: str = Field(description="Server ID.")
    name: str = Field(description="Server name.")


class FavoritesListResponse(BaseModel):
    """List of favorited servers for dashboard."""

    data: list[FavoriteServerItem] = Field(default_factory=list)


class LimitsResponse(BaseModel):
    """Per-user limits (servers, clusters) for dashboard display."""

    servers_used: int = Field(description="Number of servers owned by the user.")
    servers_limit: int = Field(description="Maximum servers allowed per user.")
    clusters_used: int = Field(description="Number of clusters owned by the user.")
    clusters_limit: int = Field(description="Maximum clusters allowed per user.")


class ConsentStateResponse(BaseModel):
    """Consent state for the current user (or for a server when viewing as owner)."""

    consent_state: Literal["inactive", "partial", "active"] = Field(
        description="inactive = no data collected; partial = server eligible, player not; active = both."
    )


@router.get("/limits", response_model=LimitsResponse)
async def get_limits(
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    Get per-user limits (servers and clusters used vs limit).

    Used by Dashboard to show "X of Y servers", "X of Y clusters", and disable Add Server / Create cluster at limit.
    Limits may be overridden per user by admin (profile.servers_limit_override, clusters_limit_override).
    """
    token = extract_bearer_token(request)
    if not token:
        settings = get_settings()
        return LimitsResponse(
            servers_used=0,
            servers_limit=settings.MAX_SERVERS_PER_USER,
            clusters_used=0,
            clusters_limit=settings.MAX_CLUSTERS_PER_USER,
        )
    servers_limit, clusters_limit = get_effective_limits(user.user_id)
    repo = get_servers_repo(token)
    servers_used = await repo.count_owner_servers(user.user_id)
    admin = get_supabase_admin()
    clusters_used = 0
    if admin:
        try:
            r = (
                admin.table("clusters")
                .select("id")
                .eq("owner_user_id", user.user_id)
                .execute()
            )
            clusters_used = len(r.data) if r.data else 0
        except Exception:
            pass
    return LimitsResponse(
        servers_used=servers_used,
        servers_limit=servers_limit,
        clusters_used=clusters_used,
        clusters_limit=clusters_limit,
    )


@router.get("/favorites", response_model=FavoritesListResponse)
async def get_my_favorites(
    request: Request,
    user: UserIdentity = Depends(require_user),
):
    """
    List servers the current user has favorited.

    Used by Dashboard "Favorites" section. Returns minimal server info (id, name).
    """
    token = extract_bearer_token(request)
    if not token:
        return FavoritesListResponse(data=[])
    client = get_rls_client(token)
    fav_result = (
        client.table("favorites")
        .select("server_id")
        .eq("user_id", user.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    if not fav_result.data:
        return FavoritesListResponse(data=[])
    server_ids = [row["server_id"] for row in fav_result.data]
    dir_result = (
        client.table("directory_view")
        .select("id,name")
        .in_("id", server_ids)
        .execute()
    )
    # Preserve order from favorites
    by_id = {row["id"]: row["name"] for row in (dir_result.data or [])}
    data = [
        FavoriteServerItem(id=sid, name=by_id.get(sid, "Unknown"))
        for sid in server_ids
        if sid in by_id
    ]
    return FavoritesListResponse(data=data)


@router.get("/consent-state", response_model=ConsentStateResponse)
async def get_consent_state(
    user: UserIdentity = Depends(require_user),
):
    """
    Get current user's consent state for data collection.

    Used by Dashboard and Consent page to show clear indicators.
    When no consent DB/plugin exists, returns "inactive"; "partial" and "active"
    will be wired when consent is implemented.
    """
    # No consent DB yet: derive inactive for everyone
    return ConsentStateResponse(consent_state="inactive")


class TermsAcceptanceResponse(BaseModel):
    """Terms acceptance timestamps for the current user."""

    terms_accepted_at: str | None = Field(description="When user accepted ToS at account creation (ISO8601).")
    server_listing_terms_accepted_at: str | None = Field(
        description="When user accepted ToS before adding first server (ISO8601)."
    )


class TermsAcceptancePostBody(BaseModel):
    """Body for recording terms acceptance."""

    acceptance_type: Literal["account", "server_listing"] = Field(
        description="Either 'account' (signup) or 'server_listing' (first server)."
    )


@router.get("/terms-acceptance", response_model=TermsAcceptanceResponse)
async def get_terms_acceptance(
    user: UserIdentity = Depends(require_user),
):
    """
    Get current user's terms acceptance timestamps.

    Used by the frontend to know whether to show ToS modals (signup vs first server).
    """
    admin = get_supabase_admin()
    if not admin:
        return TermsAcceptanceResponse(terms_accepted_at=None, server_listing_terms_accepted_at=None)

    try:
        r = (
            admin.table("profiles")
            .select("terms_accepted_at, server_listing_terms_accepted_at")
            .eq("id", user.user_id)
            .maybe_single()
            .execute()
        )
    except Exception:
        return TermsAcceptanceResponse(terms_accepted_at=None, server_listing_terms_accepted_at=None)

    row = r.data if hasattr(r, "data") else None
    if not row:
        return TermsAcceptanceResponse(terms_accepted_at=None, server_listing_terms_accepted_at=None)

    terms_at = row.get("terms_accepted_at")
    server_listing_at = row.get("server_listing_terms_accepted_at")
    return TermsAcceptanceResponse(
        terms_accepted_at=terms_at if terms_at else None,
        server_listing_terms_accepted_at=server_listing_at if server_listing_at else None,
    )


@router.post("/terms-acceptance")
async def post_terms_acceptance(
    body: TermsAcceptancePostBody,
    user: UserIdentity = Depends(require_user),
):
    """
    Record terms acceptance (account or server_listing).

    Creates profile row if it does not exist (first time). Stores timestamp for legal audit.
    """
    import datetime

    admin = get_supabase_admin()
    if not admin:
        return {"ok": False, "message": "Profile storage not configured"}

    user_id = user.user_id
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if body.acceptance_type == "account":
        column = "terms_accepted_at"
    else:
        column = "server_listing_terms_accepted_at"

    try:
        existing = (
            admin.table("profiles")
            .select("id")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        data = existing.data if hasattr(existing, "data") else None
        if data:
            admin.table("profiles").update({
                column: now_iso,
                "updated_at": now_iso,
            }).eq("id", user_id).execute()
        else:
            admin.table("profiles").insert({
                "id": user_id,
                column: now_iso,
                "created_at": now_iso,
                "updated_at": now_iso,
            }).execute()
    except Exception:
        # Race: profile created between select and insert; retry as update
        admin.table("profiles").update({
            column: now_iso,
            "updated_at": now_iso,
        }).eq("id", user_id).execute()

    return {"ok": True}


# Timeout for Supabase Auth Admin delete (avoid hanging if Supabase is slow)
ACCOUNT_DELETE_TIMEOUT_SECONDS = 25


@router.delete("")
async def delete_my_account(
    user: UserIdentity = Depends(require_user),
):
    """
    Permanently delete the current user's account and all associated data.

    Calls Supabase Auth Admin API to delete the user; DB cascades remove
    profiles, servers, clusters, favorites, and related rows. This action
    is permanent and cannot be reversed. Response may take several seconds;
    we use a timeout to avoid hanging if Supabase is slow.
    """
    admin = get_supabase_admin()
    if not admin:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="Account deletion is not available (server configuration).",
        )

    import httpx

    settings = get_settings()
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/admin/users/{user.user_id}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY or "",
    }

    try:
        async with httpx.AsyncClient(timeout=ACCOUNT_DELETE_TIMEOUT_SECONDS) as client:
            response = await client.delete(url, headers=headers)
    except httpx.TimeoutException:
        import logging

        logging.getLogger(__name__).warning(
            "Account delete timed out for user_id=%s (Supabase Auth did not respond in %ss)",
            user.user_id,
            ACCOUNT_DELETE_TIMEOUT_SECONDS,
        )
        from fastapi import HTTPException

        raise HTTPException(
            status_code=504,
            detail="Deletion is taking longer than usual. Please try again in a few minutes or contact support.",
        )
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception("Account delete failed for user_id=%s", user.user_id)
        from fastapi import HTTPException

        raise HTTPException(
            status_code=502,
            detail="Could not complete account deletion. Please try again or contact support.",
        ) from e

    if response.status_code == 200:
        return {"ok": True, "message": "Account and data have been permanently deleted."}

    # Supabase may return 404 if user already gone, or 4xx/5xx
    from fastapi import HTTPException

    if response.status_code == 404:
        # User already deleted (e.g. race) — treat as success so client can sign out
        return {"ok": True, "message": "Account and data have been permanently deleted."}
    try:
        body = response.json()
        msg = body.get("msg") or body.get("message") or response.text or "Unknown error"
    except Exception:
        msg = response.text or "Unknown error"
    raise HTTPException(
        status_code=502,
        detail=f"Account deletion could not be completed: {msg}",
    )
