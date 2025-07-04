import uuid
from pydantic import BaseModel, Field

class Risk(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    asset_id: uuid.UUID
    vulnerability_id: uuid.UUID
    scan_id: uuid.UUID
    
    impact_score: float = Field(..., alias="ic_score")
    probability_score: float = Field(..., alias="pc_score")
    risk_score: float = Field(..., alias="nr_score")
    
    class Config:
        from_attributes = True
        populate_by_name = True