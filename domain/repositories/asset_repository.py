from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from domain.entities.asset import Asset

class IAssetRepository(ABC):
    """
    Abstract interface for retrieving Asset data.
    """
    @abstractmethod
    async def find_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """
        Retrieves an asset by its ID.
        """
        pass