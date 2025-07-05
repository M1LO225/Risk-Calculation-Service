import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database settings
    ASSET_DATABASE_URL: str
    RISK_DATABASE_URL: str

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CONSUMER_GROUP: str
    KAFKA_SOURCE_TOPIC: str
    KAFKA_DESTINATION_TOPIC: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()