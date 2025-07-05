from abc import ABC, abstractmethod
from domain.entities.risk import Risk

class IMessagingProducer(ABC):
    """Abstract interface for a messaging producer."""

    @abstractmethod
    def publish_risk_calculated(self, risk: Risk) -> None:
        """Publishes an event indicating a risk has been calculated."""
        pass