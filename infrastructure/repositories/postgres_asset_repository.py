from typing import Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData

from domain.entities.asset import Asset
from domain.repositories.asset_repository import IAssetRepository

# We reflect the table from the other database instead of redefining the model
# to ensure we don't have conflicting definitions.
metadata = MetaData()
asset_table = Table('assets', metadata, autoload_with=None) # We'll bind it later

class PostgresAssetRepository(IAssetRepository):
    def __init__(self, db_session: Session):
        self.db = db_session
        # Dynamically bind the engine from the session to the metadata
        asset_table.metadata.bind = self.db.get_bind()

    def find_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        # Since we are using reflection, we construct the query carefully.
        # This assumes the table exists and has the necessary columns.
        result = self.db.execute(
            asset_table.select().where(asset_table.c.id == asset_id)
        ).first()

        if result:
            return Asset(
                id=result.id,
                scan_id=result.scan_id,
                sca_c=result.sca_c,
                sca_i=result.sca_i,
                sca_d=result.sca_d
            )
        return None