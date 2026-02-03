"""
Me / profile endpoints.

Handles current user profile and terms acceptance (legal audit).
"""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.deps import require_user
from app.core.security import UserIdentity
from app.core.supabase import get_supabase_admin

router = APIRouter(prefix="/me", tags=["me"])


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
