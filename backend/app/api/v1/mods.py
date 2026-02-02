"""
Mods endpoints.

Handles mod ID to name resolution using CurseForge API and local catalog.
"""

import logging
from typing import TypedDict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.db.mods_catalog_repo import ModCatalogEntry
from app.db.providers import get_mods_catalog_repo
from app.integrations.curseforge_client import (
    CurseForgeClient,
    get_curseforge_client,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mods", tags=["mods"])


class ModResolveRequest(BaseModel):
    """Mod resolve request."""

    mod_ids: list[int]


class ModResolveResponse(BaseModel):
    """Mod resolve response."""

    data: list[ModCatalogEntry]
    missing: list[int]


@router.post("/resolve", response_model=ModResolveResponse)
async def resolve_mods(request: ModResolveRequest) -> ModResolveResponse:
    """
    Resolve mod IDs to names.

    Looks up mods in local catalog first, then queries CurseForge for missing IDs.
    Upserts CurseForge results into local catalog.

    Args:
        request: Request with mod_ids list

    Returns:
        Response with resolved mods and missing IDs
    """
    settings = get_settings()

    # Validate API key is configured
    if not settings.CURSEFORGE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="CurseForge API key not configured. Mod resolution unavailable.",
        )

    # Validate and dedupe mod IDs
    mod_ids = request.mod_ids
    if not mod_ids:
        return {"data": [], "missing": []}

    # Validate IDs are positive integers
    validated_ids: list[int] = []
    for mod_id in mod_ids:
        try:
            mod_id_int = int(mod_id)
            if mod_id_int > 0:
                validated_ids.append(mod_id_int)
        except (ValueError, TypeError):
            logger.warning(f"Invalid mod ID: {mod_id}, skipping")
            continue

    # Dedupe
    unique_ids = list(set(validated_ids))
    if not unique_ids:
        return {"data": [], "missing": []}

    # Get repository
    catalog_repo = get_mods_catalog_repo()

    # Lookup existing mods in catalog
    catalog_names = await catalog_repo.get_many(unique_ids)

    # Find missing IDs
    missing_ids = [mod_id for mod_id in unique_ids if mod_id not in catalog_names]

    # Build result from catalog
    result: list[ModCatalogEntry] = []
    for mod_id in unique_ids:
        if mod_id in catalog_names:
            # Get full entry (we only have name from get_many, but that's enough)
            # For now, we'll return basic structure. If we need slug/source, we'd need to fetch full entries.
            result.append(
                {
                    "mod_id": mod_id,
                    "name": catalog_names[mod_id],
                    "slug": None,  # Not available from get_many
                    "source": "catalog",
                }
            )

    # Resolve missing IDs from CurseForge
    if missing_ids:
        try:
            curseforge_client = get_curseforge_client()
            curseforge_mods = await curseforge_client.get_mods_by_ids(missing_ids)

            # Upsert into catalog
            if curseforge_mods:
                catalog_entries: list[ModCatalogEntry] = []
                for mod_id, mod_data in curseforge_mods.items():
                    catalog_entries.append(
                        {
                            "mod_id": mod_id,
                            "name": mod_data["name"],
                            "slug": mod_data.get("slug"),
                            "source": "curseforge",
                        }
                    )
                    # Add to result
                    result.append(
                        {
                            "mod_id": mod_id,
                            "name": mod_data["name"],
                            "slug": mod_data.get("slug"),
                            "source": "curseforge",
                        }
                    )

                # Upsert into catalog
                await catalog_repo.upsert_many(catalog_entries)

            # Track still-missing IDs
            resolved_ids = set(curseforge_mods.keys())
            still_missing = [
                mod_id for mod_id in missing_ids if mod_id not in resolved_ids
            ]

        except Exception as e:
            logger.error(f"Failed to resolve mods from CurseForge: {str(e)}")
            # Return what we have, mark all missing as unresolved
            still_missing = missing_ids
    else:
        still_missing = []

    return {"data": result, "missing": still_missing}


@router.get("/search")
async def search_mods(q: str, limit: int = 20) -> list[ModCatalogEntry]:
    """
    Search mods by name prefix (autocomplete).

    Args:
        q: Search query (prefix)
        limit: Maximum results

    Returns:
        List of matching mod catalog entries
    """
    if not q or len(q) < 2:
        return []

    catalog_repo = get_mods_catalog_repo()
    results = await catalog_repo.search_by_prefix(q, limit=limit)
    return results
