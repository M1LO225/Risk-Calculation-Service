from abc import ABC, abstractmethod
from domain.entities.risk import Risk

class IMessagingProducer(ABC):
    """
    Abstract interface for publishing domain events.
    """
    @abstractmethod
    async def publish_risk_calculated(self, risk: Risk):
        """
        Publishes an event indicating a risk has been calculated.
        """
        pass