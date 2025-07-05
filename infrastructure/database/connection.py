from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# --- Connection for ASSET Database (Read-Only) ---
asset_engine = create_engine(settings.ASSET_DATABASE_URL)
AssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=asset_engine)

# --- Connection for RISK Database (Write) ---
risk_engine = create_engine(settings.RISK_DATABASE_URL)
RiskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=risk_engine)

# Base for defining ORM models for the RISK database
RiskBase = declarative_base()

# Dependency to get an Asset DB session
def get_asset_db():
    db = AssetSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get a Risk DB session
def get_risk_db():
    db = RiskSessionLocal()
    try:
        yield db
    finally:
        db.close()