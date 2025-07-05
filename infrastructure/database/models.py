import uuid
from sqlalchemy import Column, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

# Importamos la base declarativa del archivo de conexión del propio servicio.
# Esta base SÓLO se usará para definir las tablas que este servicio crea (RiskDB).
from .connection import RiskBase

# --- Modelos de Tablas de las que este servicio es "Dueño" (Escribe en ellas) ---

class RiskDB(RiskBase):
    """
    SQLAlchemy ORM model for the 'risks' table.
    This table is owned and managed by the Risk Calculation Service.
    """
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    vulnerability_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    ic_score = Column(Float, nullable=False)
    pc_score = Column(Float, nullable=False)
    nr_score = Column(Float, nullable=False)


# --- Modelos de Tablas que este servicio SÓLO LEE ---
#
# NOTA IMPORTANTE: Estas clases NO heredan de `RiskBase`. No queremos que este
# servicio intente crear o modificar estas tablas. Son solo para que SQLAlchemy
# entienda su estructura al construir consultas de LECTURA.
# En un proyecto real, esto podría venir de una librería compartida.

from sqlalchemy.orm import declarative_base

# Creamos una base "falsa" y temporal solo para declarar estos modelos de lectura.
ReadOnlyBase = declarative_base()

# --- Copia del Enum `AssetType` para que SQLAlchemy lo entienda ---
# Idealmente, esto también estaría en una librería compartida.
import enum
class AssetTypeEnum(enum.Enum):
    SUBDOMAIN = "SUBDOMAIN"
    IP_ADDRESS = "IP_ADDRESS"
    SERVICE = "SERVICE"
    WEBSITE = "WEBSITE"

class AssetDB(ReadOnlyBase):
    """
    Read-only declaration of the 'assets' table structure.
    """
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scan_id = Column(UUID(as_uuid=True), nullable=False)
    asset_type = Column(Enum(AssetTypeEnum), nullable=False)
    value = Column(String, nullable=False)
    discovered_at = Column(DateTime, nullable=False)
    sca = Column(Float, nullable=True)
    sca_c = Column(Float, nullable=True)
    sca_i = Column(Float, nullable=True)
    sca_d = Column(Float, nullable=True)

# --- Copia del Enum `VulnerabilityImpact` ---
class VulnerabilityImpactEnum(enum.Enum):
    NONE = "NONE"
    LOW = "LOW"
    HIGH = "HIGH"

class VulnerabilityDB(ReadOnlyBase):
    """
    Read-only declaration of the 'vulnerabilities' table structure.
    """
    __tablename__ = "vulnerabilities"

    id = Column(UUID(as_uuid=True), primary_key=True)
    asset_id = Column(UUID(as_uuid=True), nullable=False) 
    cve_id = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cvss_score = Column(Float, nullable=False)
    confidentiality_impact = Column(Enum(VulnerabilityImpactEnum), nullable=False)
    integrity_impact = Column(Enum(VulnerabilityImpactEnum), nullable=False)
    availability_impact = Column(Enum(VulnerabilityImpactEnum), nullable=False)