from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings # Importamos la configuración

# Base para los modelos declarativos de SQLAlchemy
Base = declarative_base()

# --- Configuración para la Base de Datos de Riesgos (donde este servicio escribe) ---
engine_risk_db = create_engine(settings.RISK_DATABASE_URL, pool_pre_ping=True)
RiskSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_risk_db)

# --- Configuración para la Base de Datos de Activos (donde este servicio lee) ---
# En un entorno real, estas URLs apuntarían a bases de datos distintas o réplicas.
# Aquí, por simplicidad, podrían apuntar a la misma DB física pero con esquemas/conexiones lógicas separadas.
engine_asset_db = create_engine(settings.ASSET_DATABASE_URL, pool_pre_ping=True)
AssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_asset_db)

def get_risk_db_session():
    """Dependency for getting a DB session for risk operations."""
    db = RiskSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_asset_db_session():
    """Dependency for getting a DB session for asset operations."""
    db = AssetSessionLocal()
    try:
        yield db
    finally:
        db.close()