# ... imports ...
class RiskCalculationConsumer:
    # ... constructor ...
    
    def run(self):
        # ... loop over messages ...
        
        # Here we need two different DB sessions if the databases are separate
        asset_db_session = AssetSessionLocal()
        risk_db_session = RiskSessionLocal()
        try:
            # Dependency Injection
            asset_repo = PostgresAssetRepository(asset_db_session)
            risk_repo = PostgresRiskRepository(risk_db_session)
            producer = KafkaMessagingProducer()
            formulas = RiskFormulaService()
            
            use_case = CalculateRiskUseCase(asset_repo, risk_repo, producer, formulas)
            
            # Execute
            use_case.execute(vuln_event)
        finally:
            asset_db_session.close()
            risk_db_session.close()