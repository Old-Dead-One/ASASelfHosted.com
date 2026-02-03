"""
Supabase maps repository.

Reads from public.maps table (reference list of ASA map names).
Uses anon key; maps table has public read.
"""

from app.core.supabase import get_supabase_anon
from app.db.maps_repo import MapEntry, MapsRepository


class SupabaseMapsRepository(MapsRepository):
    """
    Supabase-based maps repository.

    Uses anon key; maps table grants SELECT to anon.
    """

    def __init__(self):
        self._supabase = get_supabase_anon()

    async def list_all(self) -> list[MapEntry]:
        if self._supabase is None:
            return []

        try:
            response = (
                self._supabase.table("maps")
                .select("id,name")
                .order("sort_order")
                .order("name")
                .execute()
            )
            rows = response.data or []
            return [{"id": str(r["id"]), "name": r["name"]} for r in rows]
        except Exception:
            return []
