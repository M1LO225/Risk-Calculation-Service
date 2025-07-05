import json
import logging
from kafka import KafkaProducer

from core.config import settings
from domain.entities.risk import Risk
from domain.repositories.messaging_producer import IMessagingProducer

logger = logging.getLogger(__name__)

class KafkaMessagingProducer(IMessagingProducer):
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            logger.info("Kafka producer connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect Kafka producer: {e}")
            self.producer = None

    def publish_risk_calculated(self, risk: Risk) -> None:
        if not self.producer:
            logger.error("Kafka producer is not available. Cannot publish message.")
            return

        message = {
            "risk_id": str(risk.id),
            "scan_id": str(risk.scan_id),
            "asset_id": str(risk.asset_id),
            "risk_score": risk.risk_score
        }
        
        try:
            self.producer.send(settings.KAFKA_DESTINATION_TOPIC, value=message)
            self.producer.flush()
            logger.info(f"Published 'risk.calculated' event for risk_id: {risk.id}")
        except Exception as e:
            logger.error(f"Failed to publish message for risk_id {risk.id}: {e}")