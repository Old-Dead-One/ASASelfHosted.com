"""
Maps repository interface.

Abstract interface for listing known ASA map names (for filter and form dropdown).
"""

from abc import ABC, abstractmethod
from typing import TypedDict


class MapEntry(TypedDict):
    """Single map entry."""

    id: str
    name: str


class MapsRepository(ABC):
    """
    Abstract repository for maps (reference list of known ASA map names).
    """

    @abstractmethod
    async def list_all(self) -> list[MapEntry]:
        """
        List all maps, ordered by sort_order then name.

        Returns:
            List of { id, name } for dropdown/filter use.
        """
