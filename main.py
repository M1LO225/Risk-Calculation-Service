import asyncio
import logging
from worker.consumer import RiskCalculationConsumer

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Risk Calculation Service...")
    consumer = RiskCalculationConsumer()
    try:
        await consumer.start()
        # Keep the main loop running
        while True:
            await asyncio.sleep(3600) # Sleep for an hour, or until cancelled
    except asyncio.CancelledError:
        logger.info("Service shutdown initiated.")
    except Exception as e:
        logger.critical(f"Service crashed: {e}", exc_info=True)
    finally:
        await consumer.stop()
        logger.info("Risk Calculation Service stopped gracefully.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user.")
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)