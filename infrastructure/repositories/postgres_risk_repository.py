from sqlalchemy.orm import Session
import logging

from domain.entities.risk import Risk
from domain.repositories.risk_repository import IRiskRepository
from infrastructure.database.models import RiskDB

logger = logging.getLogger(__name__)

class PostgresRiskRepository(IRiskRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def save(self, risk: Risk) -> Risk:
        risk_db = RiskDB(
            id=risk.id,
            scan_id=risk.scan_id,
            asset_id=risk.asset_id,
            vulnerability_id=risk.vulnerability_id,
            ic_score=risk.impact_score,
            pc_score=risk.probability_score,
            nr_score=risk.risk_score
        )
        self.db.add(risk_db)
        self.db.commit()
        self.db.refresh(risk_db)
        logger.info(f"Saved new risk {risk.id} with score {risk.risk_score} to the database.")
        # Use .from_orm() to map back to the Pydantic model with aliases
        return Risk.from_orm(risk_db)