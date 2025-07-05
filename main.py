from worker.consumer import RiskCalculationConsumer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def start_worker():
    """Inicializa y corre el worker."""
    try:
        worker = RiskCalculationConsumer()
        worker.run()
    except Exception as e:
        logging.critical(f"El worker ha fallado al iniciar: {e}", exc_info=True)

if __name__ == "__main__":
    start_worker()