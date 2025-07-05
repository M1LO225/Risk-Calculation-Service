import json
import logging
from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import ValidationError

# 1. Importaciones Clave
from core.config import settings
from domain.entities.vulnerability_event import VulnerabilityFoundEvent
from application.use_cases.calculate_risk import CalculateRiskUseCase
from application.services.risk_formula_service import RiskFormulaService
from infrastructure.repositories.postgres_asset_repository import PostgresAssetRepository
from infrastructure.repositories.postgres_risk_repository import PostgresRiskRepository
from infrastructure.messaging.kafka_producer import KafkaMessagingProducer

# Configuración del Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2. Configuración para AMBAS bases de datos (de forma síncrona)
# Conexión a la base de datos de RIESGOS (para escribir)
engine_risk_db = create_engine(settings.RISK_DATABASE_URL)
RiskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_risk_db)

# Conexión a la base de datos de ACTIVOS (para leer)
engine_asset_db = create_engine(settings.ASSET_DATABASE_URL)
AssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_asset_db)


class RiskCalculationConsumer:
    def __init__(self):
        """Inicializa el consumidor síncrono de Kafka."""
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_SOURCE_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
        except Exception as e:
            logger.critical(f"No se pudo conectar a Kafka: {e}")
            # En un caso real, podrías querer reintentar o salir del programa
            raise

    def run(self):
        """Inicia el bucle para consumir mensajes."""
        logger.info(f"Worker iniciado. Escuchando mensajes en el topic '{settings.KAFKA_SOURCE_TOPIC}'...")
        
        for message in self.consumer:
            logger.info(f"Mensaje recibido: {message.value}")
            
            try:
                # Validar el evento de entrada con Pydantic
                vuln_event = VulnerabilityFoundEvent(**message.value)
            except ValidationError as e:
                logger.error(f"Formato de mensaje inválido: {e}. Saltando mensaje.")
                continue

            # 3. Crear sesiones para ambas bases de datos por cada mensaje
            risk_db_session: Session = RiskSessionLocal()
            asset_db_session: Session = AssetSessionLocal()
            try:
                # 4. Inyección de Dependencias
                asset_repo = PostgresAssetRepository(asset_db_session)
                risk_repo = PostgresRiskRepository(risk_db_session)
                producer = KafkaMessagingProducer()
                formula_service = RiskFormulaService()
                
                use_case = CalculateRiskUseCase(
                    asset_repo=asset_repo,
                    risk_repo=risk_repo,
                    messaging_producer=producer,
                    formula_service=formula_service
                )
                
                # 5. Ejecutar el caso de uso
                use_case.execute(vuln_event)
                
                logger.info(f"Mensaje procesado exitosamente para la vulnerabilidad: {vuln_event.vulnerability_id}")

            except Exception as e:
                logger.error(f"Ocurrió un error al procesar la vulnerabilidad {vuln_event.vulnerability_id}: {e}", exc_info=True)
            finally:
                # 6. Asegurarse de cerrar ambas sesiones
                risk_db_session.close()
                asset_db_session.close()