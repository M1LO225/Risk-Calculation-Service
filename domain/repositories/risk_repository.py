from abc import ABC, abstractmethod
from domain.entities.risk import Risk

class IRiskRepository(ABC):
    """Abstract interface for risk data persistence."""

    @abstractmethod
    def save(self, risk: Risk) -> Risk:
        """Saves a risk entity."""
        pass