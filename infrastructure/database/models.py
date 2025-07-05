import uuid
from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from infrastructure.database.connection import Base # Assumes a connection for the risk_db

class RiskDB(Base):
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    vulnerability_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    ic_score = Column(Float, nullable=False)
    pc_score = Column(Float, nullable=False)
    nr_score = Column(Float, nullable=False)

class AssetDB(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    vulnerability_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    ic_score = Column(Float, nullable=False)
    pc_score = Column(Float, nullable=False)
    nr_score = Column(Float, nullable=False)