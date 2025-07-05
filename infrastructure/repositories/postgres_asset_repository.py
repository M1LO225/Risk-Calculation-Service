import logging
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from domain.entities.asset import Asset
from domain.repositories.asset_repository import IAssetRepository


logger = logging.getLogger(__name__)

class PostgresAssetRepository(IAssetRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def find_by_id(self, asset_id: UUID) -> Optional[Asset]:
        """
        Retrieves an asset by its ID from the asset database.
        Note: This is a simplified read; in a full system, you'd define 
        a proper AssetDB model if you were directly querying asset data here.
        For this project, we assume asset valuation scores (SCA_C, I, D) 
        are directly available on the asset record.
        """
        try:

            
            from infrastructure.database.models import AssetDB # Assuming a model will be here
            asset_db_model = self.db_session.query(AssetDB).filter(AssetDB.id == asset_id).first()

            if asset_db_model:
                # Map the DB model attributes to the domain entity
                return Asset(
                    id=asset_db_model.id,
                    scan_id=asset_db_model.scan_id,
                    sca_c=asset_db_model.sca_c,
                    sca_i=asset_db_model.sca_i,
                    sca_d=asset_db_model.sca_d,
                )
            return None
        except Exception as e:
            logger.error(f"Error finding asset {asset_id}: {e}")
            raise # Re-raise to be handled by the consumer's error logic