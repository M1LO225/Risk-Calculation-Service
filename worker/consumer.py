import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


from domain.entities.vulnerability_event import VulnerabilityFoundEvent
# Make sure your models are imported for Base.metadata.create_all
from infrastructure.database.models import Base # Assuming your RiskDB model is here
from infrastructure.repositories.postgres_asset_repository import PostgresAssetRepository
from infrastructure.repositories.postgres_risk_repository import PostgresRiskRepository
from infrastructure.messaging.kafka_producer import KafkaMessagingProducer
from application.services.risk_formula_service import RiskFormulaService
from application.use_cases.calculate_risk import CalculateRiskUseCase

logger = logging.getLogger(__name__)

# Configura logging si no está ya configurado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Async Database Setup ---
# Use async_scoped_session for managing sessions in async contexts if using FastAPI,
# but for a simple worker, direct async sessionmakers are fine.
engine_risk_db_async = create_async_engine(settings.RISK_DATABASE_URL, pool_pre_ping=True)
AsyncRiskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_risk_db_async, class_=AsyncSession)

engine_asset_db_async = create_async_engine(settings.ASSET_DATABASE_URL, pool_pre_ping=True)
AsyncAssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_asset_db_async, class_=AsyncSession)

# Async session getters
async def get_async_risk_db_session():
    async with AsyncRiskSessionLocal() as session:
        yield session

async def get_async_asset_db_session():
    async with AsyncAssetSessionLocal() as session:
        yield session

class RiskCalculationConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_SOURCE_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        self.producer = KafkaMessagingProducer() # KafkaMessagingProducer already handles its start/stop
        self.formula_service = RiskFormulaService()
        self.running = False

    async def _setup_database(self):
        """Ensures the database table for risks exists."""
        async with engine_risk_db_async.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database setup complete: 'risks' table ensured.")

    async def start(self):
        """Starts the Kafka consumer, producer, and begins message consumption."""
        self.running = True
        await self._setup_database()
        await self.consumer.start()
        await self.producer.start() # Start Kafka producer
        logger.info(f"Kafka consumer started for topic: {settings.KAFKA_SOURCE_TOPIC}")
        
        # Start consuming messages
        await self.consume_messages()

    async def stop(self):
        """Stops the Kafka consumer and producer gracefully."""
        self.running = False
        await self.consumer.stop()
        await self.producer.stop() # Stop Kafka producer
        logger.info("Kafka consumer and producer stopped.")

    async def consume_messages(self):
        """
        Continuously consumes messages from Kafka and processes them.
        """
        try:
            async for msg in self.consumer:
                if not self.running:
                    logger.info("Consumer stopping due to shutdown signal.")
                    break

                logger.info(f"Received message: Topic={msg.topic}, Partition={msg.partition}, Offset={msg.offset}")
                
                # Use async context managers for sessions
                async with AsyncAssetSessionLocal() as asset_db_session, \
                           AsyncRiskSessionLocal() as risk_db_session:
                    try:
                        event_data = json.loads(msg.value.decode('utf-8'))
                        vuln_event = VulnerabilityFoundEvent(**event_data)
                        logger.info(f"Processing vulnerability event for asset_id: {vuln_event.asset_id}, CVE: {vuln_event.cve_id}")

                        # Dependency Injection
                        asset_repo = PostgresAssetRepository(asset_db_session)
                        risk_repo = PostgresRiskRepository(risk_db_session)
                        
                        use_case = CalculateRiskUseCase(asset_repo, risk_repo, self.producer, self.formula_service)
                        
                        # Execute the use case
                        await use_case.execute(vuln_event)

                        # Commit the offset manually after successful processing
                        await self.consumer.commit({"topic_partition": msg.topic_partition, "offset": msg.offset + 1})
                        logger.info(f"Successfully processed message and committed offset {msg.offset + 1}")

                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON from message: {e}. Message: {msg.value.decode('utf-8')}")
                        # In production, you might send to a DLQ or log for manual review,
                        # and then commit the offset to prevent reprocessing bad messages.
                        await self.consumer.commit({"topic_partition": msg.topic_partition, "offset": msg.offset + 1})
                    except SQLAlchemyError as e:
                        logger.error(f"Database error during message processing for asset_id {vuln_event.asset_id if 'vuln_event' in locals() else 'N/A'}: {e}")
                        # If a DB error, don't commit offset so message is reprocessed (assuming transient error)
                        await risk_db_session.rollback() # Ensure rollback
                    except Exception as e:
                        logger.error(f"Unhandled error processing message for asset_id {vuln_event.asset_id if 'vuln_event' in locals() else 'N/A'}: {e}", exc_info=True)
                        # Don't commit offset for unhandled errors
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled.")
        except Exception as e:
            logger.critical(f"Critical error in consumer loop: {e}", exc_info=True)