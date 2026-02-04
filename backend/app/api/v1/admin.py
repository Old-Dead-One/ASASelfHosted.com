"""
Admin-only endpoints.

Sprint 8: Rejection summary, server overrides (hide/unhide, badges_frozen), incident notes.
All routes require user to be in ADMIN_USER_IDS.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.deps import require_admin
from app.core.security import UserIdentity
from app.core.supabase import get_supabase_admin

router = APIRouter(prefix="/admin", tags=["admin"])


class RejectionsSummaryResponse(BaseModel):
    """Aggregate counts of ingest rejections by reason."""

    by_reason: dict[str, int] = Field(description="Count per rejection_reason.")
    total: int = Field(description="Total rejections in window.")


@router.get("/rejections-summary", response_model=RejectionsSummaryResponse)
async def get_rejections_summary(
    user: UserIdentity = Depends(require_admin),
):
    """
    Get summary of ingest rejections (e.g. last 24h or all time).

    Admin-only. No PII; aggregate counts by rejection_reason.
    """
    admin = get_supabase_admin()
    if not admin:
        return RejectionsSummaryResponse(by_reason={}, total=0)

    try:
        r = (
            admin.table("ingest_rejections")
            .select("rejection_reason")
            .order("received_at", desc=True)
            .limit(5000)
            .execute()
        )
    except Exception:
        return RejectionsSummaryResponse(by_reason={}, total=0)

    data = r.data if hasattr(r, "data") else []
    by_reason: dict[str, int] = {}
    for row in data:
        reason = row.get("rejection_reason") or "unknown"
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return RejectionsSummaryResponse(by_reason=by_reason, total=len(data))


class ServerOverrideBody(BaseModel):
    """Admin override for a server."""

    hidden_at: datetime | None = Field(default=None, description="When set, server is hidden from directory. Null to unhide.")
    badges_frozen: bool | None = Field(default=None, description="When true, worker does not update badge/ranking fields.")


@router.patch("/servers/{server_id}")
async def admin_update_server(
    server_id: str,
    body: ServerOverrideBody,
    user: UserIdentity = Depends(require_admin),
):
    """
    Admin override: hide/unhide server, or set badges_frozen.

    Only fields present in body are updated. directory_view excludes servers with hidden_at set.
    """
    admin = get_supabase_admin()
    if not admin:
        return {"ok": False, "message": "Backend not configured"}

    payload: dict = {}
    if body.hidden_at is not None:
        payload["hidden_at"] = body.hidden_at.isoformat() if body.hidden_at else None
    if body.badges_frozen is not None:
        payload["badges_frozen"] = body.badges_frozen

    if not payload:
        return {"ok": True, "message": "No changes"}

    try:
        admin.table("servers").update(payload).eq("id", server_id).execute()
    except Exception as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True}


class IncidentNoteCreate(BaseModel):
    """Create an incident note."""

    server_id: str | None = Field(default=None, description="Associated server.")
    cluster_id: str | None = Field(default=None, description="Associated cluster.")
    note_text: str = Field(..., min_length=1)
    internal_only: bool = True


class IncidentNoteOut(BaseModel):
    """Incident note (admin view)."""

    id: str
    server_id: str | None
    cluster_id: str | None
    author_id: str
    note_text: str
    internal_only: bool
    created_at: str


@router.post("/incident-notes", response_model=IncidentNoteOut)
async def create_incident_note(
    body: IncidentNoteCreate,
    user: UserIdentity = Depends(require_admin),
):
    """Create an incident note (admin-only)."""
    admin = get_supabase_admin()
    if not admin:
        raise HTTPException(status_code=503, detail="Backend not configured")

    row = {
        "author_id": user.user_id,
        "note_text": body.note_text,
        "internal_only": body.internal_only,
    }
    if body.server_id:
        row["server_id"] = body.server_id
    if body.cluster_id:
        row["cluster_id"] = body.cluster_id

    r = admin.table("incident_notes").insert(row).execute()
    data = r.data[0] if r.data else {}
    return IncidentNoteOut(
        id=data["id"],
        server_id=data.get("server_id"),
        cluster_id=data.get("cluster_id"),
        author_id=data["author_id"],
        note_text=data["note_text"],
        internal_only=data.get("internal_only", True),
        created_at=data["created_at"],
    )


@router.get("/incident-notes", response_model=list[IncidentNoteOut])
async def list_incident_notes(
    server_id: str | None = None,
    cluster_id: str | None = None,
    user: UserIdentity = Depends(require_admin),
):
    """List incident notes (admin-only). Filter by server_id or cluster_id."""
    admin = get_supabase_admin()
    if not admin:
        return []

    q = admin.table("incident_notes").select("*").order("created_at", desc=True).limit(200)
    if server_id:
        q = q.eq("server_id", server_id)
    if cluster_id:
        q = q.eq("cluster_id", cluster_id)
    r = q.execute()
    data = r.data if hasattr(r, "data") else []
    return [
        IncidentNoteOut(
            id=row["id"],
            server_id=row.get("server_id"),
            cluster_id=row.get("cluster_id"),
            author_id=row["author_id"],
            note_text=row["note_text"],
            internal_only=row.get("internal_only", True),
            created_at=row["created_at"],
        )
        for row in data
    ]


class ProfileLimitsBody(BaseModel):
    """Admin override for a user's servers/clusters limits."""

    servers_limit_override: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Max servers for this user. Null to clear override (use config default).",
    )
    clusters_limit_override: int | None = Field(
        default=None,
        ge=0,
        le=50,
        description="Max clusters for this user. Null to clear override (use config default).",
    )


@router.patch("/profiles/{user_id}/limits")
async def admin_set_profile_limits(
    user_id: str,
    body: ProfileLimitsBody,
    user: UserIdentity = Depends(require_admin),
):
    """
    Set per-user limit overrides (servers, clusters).

    Admin-only. Updates profile.servers_limit_override and/or clusters_limit_override.
    Pass null to clear an override so the user gets config defaults again.
    """
    admin = get_supabase_admin()
    if not admin:
        raise HTTPException(status_code=503, detail="Backend not configured")

    payload: dict = {}
    if body.servers_limit_override is not None:
        payload["servers_limit_override"] = body.servers_limit_override
    if body.clusters_limit_override is not None:
        payload["clusters_limit_override"] = body.clusters_limit_override

    if not payload:
        return {"ok": True, "message": "No changes"}

    try:
        admin.table("profiles").update(payload).eq("id", user_id).execute()
    except Exception as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True}
