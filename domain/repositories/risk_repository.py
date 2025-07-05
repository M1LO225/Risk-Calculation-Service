from abc import ABC, abstractmethod
from domain.entities.risk import Risk

class IRiskRepository(ABC):
    """
    Abstract interface for persisting Risk entities.
    """
    @abstractmethod
    async def save(self, risk: Risk) -> Risk:
        """
        Saves a new Risk entity to the persistence layer.
        Returns the saved Risk entity, possibly with an updated ID.
        """
        pass