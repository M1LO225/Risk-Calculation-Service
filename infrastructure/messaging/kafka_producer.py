import json
import logging
from uuid import UUID
from aiokafka import AIOKafkaProducer
from domain.repositories.messaging_producer import IMessagingProducer
from domain.entities.risk import Risk
from core.config import settings

logger = logging.getLogger(__name__)

class KafkaMessagingProducer(IMessagingProducer):
    def __init__(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        self.destination_topic = settings.KAFKA_DESTINATION_TOPIC
        logger.info(f"KafkaProducer initialized for topic: {self.destination_topic}")

    async def start(self):
        """Starts the Kafka producer."""
        await self.producer.start()
        logger.info("Kafka Producer started.")

    async def stop(self):
        """Stops the Kafka producer."""
        await self.producer.stop()
        logger.info("Kafka Producer stopped.")

    async def publish_risk_calculated(self, risk: Risk):
        """
        Publishes a risk.calculated event to Kafka.
        """
        try:
            # Convert UUIDs to string for JSON serialization
            risk_dict = risk.model_dump()
            risk_dict['id'] = str(risk.id)
            risk_dict['asset_id'] = str(risk.asset_id)
            risk_dict['vulnerability_id'] = str(risk.vulnerability_id)
            risk_dict['scan_id'] = str(risk.scan_id)
            
            message = json.dumps(risk_dict).encode('utf-8')
            
            # Use risk_id as key for consistent partitioning if needed
            key = str(risk.id).encode('utf-8') 
            
            await self.producer.send_and_wait(self.destination_topic, value=message, key=key)
            logger.info(f"Published risk.calculated event for risk ID: {risk.id} to topic {self.destination_topic}")
        except Exception as e:
            logger.error(f"Failed to publish risk.calculated event for {risk.id}: {e}")
            # Depending on error handling strategy, might re-raise or log more details