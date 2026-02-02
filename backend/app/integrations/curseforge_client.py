"""
CurseForge API client.

Minimal client for resolving mod IDs to names for Ark: Survival Ascended.
"""

import asyncio
import logging
from typing import TypedDict

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CurseForgeMod(TypedDict, total=False):
    """CurseForge mod data."""

    id: int
    name: str
    slug: str  # Optional


class CurseForgeClient:
    """
    CurseForge API client.

    Handles authentication and API calls to CurseForge REST API.
    """

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.CURSEFORGE_API_KEY
        self._base_url = settings.CURSEFORGE_BASE_URL
        self._asa_game_id = settings.CURSEFORGE_ASA_GAME_ID

        if not self._api_key:
            logger.warning(
                "CURSEFORGE_API_KEY not set. CurseForge mod resolution will fail."
            )

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Accept": "application/json",
                "x-api-key": self._api_key,
            },
            timeout=30.0,
        )

    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()

    async def get_games(
        self, page_size: int = 50, index: int = 0
    ) -> tuple[list[dict], dict]:
        """
        Get games from CurseForge.

        Args:
            page_size: Number of games per page
            index: Page index (0-based)

        Returns:
            Tuple of (list of game dictionaries, pagination info)
        """
        if not self._api_key:
            raise RuntimeError("CURSEFORGE_API_KEY not configured")

        try:
            response = await self._client.get(
                "/v1/games",
                params={"pageSize": page_size, "index": index},
            )
            response.raise_for_status()
            data = response.json()
            games = data.get("data", [])
            pagination = data.get("pagination", {})
            return games, pagination
        except httpx.HTTPStatusError as e:
            logger.error(f"CurseForge API error getting games: {e.response.text}")
            raise RuntimeError(f"CurseForge API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Failed to fetch games from CurseForge: {str(e)}")
            raise RuntimeError(f"Failed to fetch games: {str(e)}") from e

    async def find_asa_game_id(self) -> int:
        """
        Get Ark: Survival Ascended game ID.

        Returns the configured game ID or the known default (83374).

        Returns:
            ASA game ID (default: 83374)
        """
        if self._asa_game_id:
            return self._asa_game_id

        # Use known game ID directly - no need to search
        # The game ID for Ark: Survival Ascended is 83374
        known_game_id = 83374
        logger.info(
            f"Using known Ark: Survival Ascended game ID: {known_game_id}. "
            f"Set CURSEFORGE_ASA_GAME_ID={known_game_id} in your .env file to skip this message."
        )
        return known_game_id

    async def get_mods_by_ids(
        self, mod_ids: list[int]
    ) -> dict[int, CurseForgeMod]:
        """
        Get mods by IDs (batch).

        Args:
            mod_ids: List of mod IDs to fetch

        Returns:
            Dictionary mapping mod_id -> mod data
        """
        if not self._api_key:
            raise RuntimeError("CURSEFORGE_API_KEY not configured")

        if not mod_ids:
            return {}

        # CurseForge API has limits, chunk requests
        batch_size = 100
        result: dict[int, CurseForgeMod] = {}

        for i in range(0, len(mod_ids), batch_size):
            batch = mod_ids[i : i + batch_size]

            try:
                response = await self._client.post(
                    "/v1/mods",
                    json={"modIds": batch},
                )
                response.raise_for_status()
                data = response.json()
                mods = data.get("data", [])

                for mod in mods:
                    mod_id = mod.get("id")
                    if mod_id:
                        slug = mod.get("slug")
                        result[int(mod_id)] = {
                            "id": int(mod_id),
                            "name": str(mod.get("name", "")),
                            "slug": str(slug) if slug else "",
                        }

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"CurseForge API error getting mods: {e.response.text}"
                )
                # Continue with other batches, but log error
                continue
            except Exception as e:
                logger.error(f"Failed to fetch mods from CurseForge: {str(e)}")
                # Continue with other batches
                continue

        return result

    async def search_mods(
        self,
        game_id: int,
        class_id: int | None = None,
        category_id: int | None = None,
        page_size: int = 50,
        sort_field: str = "Popularity",
    ) -> list[CurseForgeMod]:
        """
        Search mods.

        Args:
            game_id: Game ID
            class_id: Optional class ID
            category_id: Optional category ID
            page_size: Results per page
            sort_field: Sort field (e.g., "Popularity", "LastUpdated")

        Returns:
            List of mod data
        """
        if not self._api_key:
            raise RuntimeError("CURSEFORGE_API_KEY not configured")

        params: dict[str, int | str] = {
            "gameId": game_id,
            "pageSize": page_size,
            "sortField": sort_field,
        }
        if class_id is not None:
            params["classId"] = class_id
        if category_id is not None:
            params["categoryId"] = category_id

        try:
            response = await self._client.get(
                "/v1/mods/search",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            mods = data.get("data", [])

            result: list[CurseForgeMod] = []
            for mod in mods:
                mod_id = mod.get("id")
                if mod_id:
                    slug = mod.get("slug")
                    result.append(
                        {
                            "id": int(mod_id),
                            "name": str(mod.get("name", "")),
                            "slug": str(slug) if slug else "",
                        }
                    )

            return result
        except httpx.HTTPStatusError as e:
            logger.error(
                f"CurseForge API error searching mods: {e.response.text}"
            )
            raise RuntimeError(
                f"CurseForge API error: {e.response.status_code}"
            ) from e
        except Exception as e:
            logger.error(f"Failed to search mods from CurseForge: {str(e)}")
            raise RuntimeError(f"Failed to search mods: {str(e)}") from e

    async def get_categories(
        self, game_id: int, class_id: int | None = None
    ) -> list[dict]:
        """
        Get categories for a game.

        Args:
            game_id: Game ID
            class_id: Optional class ID

        Returns:
            List of category dictionaries
        """
        if not self._api_key:
            raise RuntimeError("CURSEFORGE_API_KEY not configured")

        params: dict[str, int] = {"gameId": game_id}
        if class_id is not None:
            params["classId"] = class_id

        try:
            response = await self._client.get(
                "/v1/categories",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except httpx.HTTPStatusError as e:
            logger.error(
                f"CurseForge API error getting categories: {e.response.text}"
            )
            raise RuntimeError(
                f"CurseForge API error: {e.response.status_code}"
            ) from e
        except Exception as e:
            logger.error(f"Failed to fetch categories from CurseForge: {str(e)}")
            raise RuntimeError(f"Failed to fetch categories: {str(e)}") from e


# Global client instance (lazy initialization)
_client: CurseForgeClient | None = None


def get_curseforge_client() -> CurseForgeClient:
    """
    Get global CurseForge client instance.

    Returns:
        CurseForgeClient instance
    """
    global _client
    if _client is None:
        _client = CurseForgeClient()
    return _client
