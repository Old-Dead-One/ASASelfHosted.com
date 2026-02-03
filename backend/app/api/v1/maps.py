"""
Maps endpoints.

Returns reference list of known ASA map names for form dropdown and directory filter.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.maps_repo import MapEntry, MapsRepository
from app.db.providers import get_maps_repo

router = APIRouter(prefix="/maps", tags=["maps"])


class MapsResponse(BaseModel):
    """Maps list response."""

    data: list[MapEntry]


@router.get("", response_model=MapsResponse)
async def list_maps(
    repo: MapsRepository = Depends(get_maps_repo),
) -> MapsResponse:
    """
    List all known map names.

    Used by ServerForm dropdown and directory filter options.
    Sourced from maps table (seeded with official ASA maps).
    """
    items = await repo.list_all()
    return MapsResponse(data=items)
