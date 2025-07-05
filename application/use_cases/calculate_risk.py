import logging

from domain.entities.risk import Risk
from domain.entities.vulnerability_event import VulnerabilityFoundEvent
from domain.repositories.asset_repository import IAssetRepository
from domain.repositories.risk_repository import IRiskRepository
from domain.repositories.messaging_producer import IMessagingProducer
from application.services.risk_formula_service import RiskFormulaService

logger = logging.getLogger(__name__)

class CalculateRiskUseCase:
    def __init__(
        self,
        asset_repo: IAssetRepository,
        risk_repo: IRiskRepository,
        messaging_producer: IMessagingProducer,
        formula_service: RiskFormulaService
    ):
        self.asset_repo = asset_repo
        self.risk_repo = risk_repo
        self.messaging_producer = messaging_producer
        self.formula_service = formula_service

    def execute(self, event: VulnerabilityFoundEvent) -> None:
        logger.info(f"Executing risk calculation for vulnerability_id: {event.vulnerability_id}")

        # 1. Fetch the required asset data
        asset = self.asset_repo.find_by_id(event.asset_id)
        if not asset:
            logger.error(f"Asset with ID {event.asset_id} not found. Cannot calculate risk.")
            return

        # 2. Perform the calculation
        risk_scores = self.formula_service.calculate_risk(asset, event)

        # 3. Create the risk entity
        new_risk = Risk(
            asset_id=event.asset_id,
            vulnerability_id=event.vulnerability_id,
            scan_id=asset.scan_id,
            ic_score=risk_scores["ic_score"],
            pc_score=risk_scores["pc_score"],
            nr_score=risk_scores["nr_score"]
        )

        # 4. Save the calculated risk
        saved_risk = self.risk_repo.save(new_risk)
        logger.info(f"Saved new risk record: {saved_risk.id} with NR score: {saved_risk.risk_score}")

        # 5. Publish the final result (optional, but good for real-time dashboards)
        self.messaging_producer.publish_risk_calculated(saved_risk)