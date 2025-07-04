import logging
from typing import Dict

from domain.entities.asset import Asset
from domain.entities.vulnerability_event import VulnerabilityFoundEvent

logger = logging.getLogger(__name__)

class RiskFormulaService:
    """
    Encapsulates the core risk calculation formulas from the methodology.
    """

    def _map_impact_to_numeric(self, impact_str: str) -> int:
        """Maps CVSS Impact (None, Low, High) to a numeric value 0, 1, 2."""
        mapping = {"NONE": 0, "LOW": 1, "HIGH": 2}
        return mapping.get(impact_str.upper(), 0)

    def calculate_ic(self, asset: Asset, vuln_event: VulnerabilityFoundEvent) -> float:
        """Calculates Impacto Cuantitativo (IC)."""
        sca_c = asset.sca_c or 0.0
        sca_i = asset.sca_i or 0.0
        sca_d = asset.sca_d or 0.0

        v_c = self._map_impact_to_numeric(vuln_event.confidentiality_impact.value)
        v_i = self._map_impact_to_numeric(vuln_event.integrity_impact.value)
        v_d = self._map_impact_to_numeric(vuln_event.availability_impact.value)

        # Formula: Ponderacion_dim = SCA_dim * V_dim
        ponderacion_c = sca_c * v_c
        ponderacion_i = sca_i * v_i
        ponderacion_d = sca_d * v_d

        # Formula: IC = (P_C + P_I + P_D) / 3 
        # The methodology doesn't specify how to scale this back to 0-10,
        # so we'll divide by 6 (max possible Ponderacion is 10*2=20, so max sum is 60,
        # 60/6 = 10) to normalize the score.
        ic_raw = (ponderacion_c + ponderacion_i + ponderacion_d)
        ic_scaled = ic_raw / 6.0
        
        return min(ic_scaled, 10.0) # Cap at 10

    def calculate_pc(self, vuln_event: VulnerabilityFoundEvent) -> float:
        """Calculates Probabilidad Cuantitativa (PC)."""
        sv = vuln_event.cvss_score
        
        # Efectividad del Control (EC). This should ideally come from another system
        # or be configurable. We'll use a placeholder value.
        ec = 0.2 # Assuming 20% effective controls are in place by default.
        
        # Formula from doc: PC = (SV / 10) * (1 - EC) -- I've corrected this from your original doc
        pc = (sv / 10.0) * (1 - ec)
        return pc

    def calculate_risk(self, asset: Asset, vuln_event: VulnerabilityFoundEvent) -> Dict[str, float]:
        """Calculates all risk scores and returns them in a dictionary."""
        logger.info(f"Calculating risk for vuln {vuln_event.cve_id} on asset {asset.id}")
        
        ic_score = self.calculate_ic(asset, vuln_event)
        pc_score = self.calculate_pc(vuln_event)
        
        # Formula: NR = IC * PC
        nr_score = ic_score * pc_score
        
        result = {
            "ic_score": round(ic_score, 2),
            "pc_score": round(pc_score, 2),
            "nr_score": round(nr_score, 2),
        }
        logger.info(f"Calculation result: {result}")
        return result