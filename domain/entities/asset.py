import uuid
from typing import Optional
from pydantic import BaseModel

class Asset(BaseModel):
    """A lean representation of the Asset needed by this service."""
    id: uuid.UUID
    scan_id: uuid.UUID
    sca_c: Optional[float]
    sca_i: Optional[float]
    sca_d: Optional[float]

    class Config:
        from_attributes = True