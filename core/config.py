from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    ASSET_DATABASE_URL: str
    RISK_DATABASE_URL: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CONSUMER_GROUP: str = "vulnerability-scanner-group"
    KAFKA_SOURCE_TOPIC: str = "asset.valuated"
    KAFKA_DESTINATION_TOPIC: str = "vulnerability.found"
    
    # NVD
    NVD_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()