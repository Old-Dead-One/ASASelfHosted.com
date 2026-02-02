"""
Mods catalog repository interface.

Abstract interface for mod ID to name resolution.
"""

from abc import ABC, abstractmethod
from typing import TypedDict


class ModCatalogEntry(TypedDict):
    """Mod catalog entry."""

    mod_id: int
    name: str
    slug: str | None
    source: str


class ModsCatalogRepository(ABC):
    """
    Abstract repository for mods catalog.

    Provides mod ID to name resolution.
    """

    @abstractmethod
    async def get_many(self, mod_ids: list[int]) -> dict[int, str]:
        """
        Get mod names for multiple mod IDs.

        Args:
            mod_ids: List of mod IDs to look up

        Returns:
            Dictionary mapping mod_id -> name. Missing IDs are omitted.
        """

    @abstractmethod
    async def upsert_many(
        self,
        entries: list[ModCatalogEntry],
    ) -> None:
        """
        Upsert multiple mod catalog entries.

        Args:
            entries: List of mod catalog entries to upsert
        """

    @abstractmethod
    async def search_by_prefix(
        self, query: str, limit: int = 20
    ) -> list[ModCatalogEntry]:
        """
        Search mods by name prefix (for autocomplete).

        Args:
            query: Search query (prefix)
            limit: Maximum number of results

        Returns:
            List of matching mod catalog entries
        """
