from abc import ABC, abstractmethod
from typing import Optional
import uuid

from domain.entities.asset import Asset

class IAssetRepository(ABC):
    """Abstract interface to get asset data from another context."""

    @abstractmethod
    def find_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        """Finds an asset by its unique ID."""
        pass