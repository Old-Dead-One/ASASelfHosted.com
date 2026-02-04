"""
Servers repository interface.

Abstract interface for server CRUD operations.
Uses RLS client for authenticated operations.
"""

from abc import ABC, abstractmethod
from typing import Sequence

from app.schemas.directory import DirectoryServer
from app.schemas.servers import ServerCreateRequest, ServerUpdateRequest


class ServersRepository(ABC):
    """
    Abstract repository for server CRUD operations.

    Implementations:
    - SupabaseServersRepository: Real Supabase queries with RLS
    """

    @abstractmethod
    async def create_server(
        self, user_id: str, server_data: ServerCreateRequest
    ) -> DirectoryServer:
        """
        Create a new server.

        Args:
            user_id: Owner user ID
            server_data: Server creation data

        Returns:
            Created server (DirectoryServer from directory_view)

        Raises:
            DomainValidationError if validation fails
        """
        pass

    @abstractmethod
    async def get_server(
        self, server_id: str, user_id: str | None = None
    ) -> DirectoryServer | None:
        """
        Get server by ID.

        Args:
            server_id: Server ID
            user_id: Optional user ID (for owner view)

        Returns:
            Server if found, None otherwise
        """
        pass

    @abstractmethod
    async def count_owner_servers(self, user_id: str) -> int:
        """
        Count servers owned by a user.

        Args:
            user_id: Owner user ID

        Returns:
            Number of servers owned by user
        """
        pass

    @abstractmethod
    async def list_owner_servers(
        self, user_id: str
    ) -> Sequence[DirectoryServer]:
        """
        List all servers owned by a user.

        Args:
            user_id: Owner user ID

        Returns:
            List of servers owned by user
        """
        pass

    @abstractmethod
    async def update_server(
        self, server_id: str, user_id: str, server_data: ServerUpdateRequest
    ) -> DirectoryServer | None:
        """
        Update server.

        Args:
            server_id: Server ID
            user_id: Owner user ID (for ownership verification)
            server_data: Update data

        Returns:
            Updated server if found and owned, None otherwise

        Raises:
            NotFoundError if server not found
            UnauthorizedError if user doesn't own server
        """
        pass

    @abstractmethod
    async def delete_server(
        self, server_id: str, user_id: str
    ) -> bool:
        """
        Delete server.

        Args:
            server_id: Server ID
            user_id: Owner user ID (for ownership verification)

        Returns:
            True if deleted, False if not found

        Raises:
            UnauthorizedError if user doesn't own server
        """
        pass
