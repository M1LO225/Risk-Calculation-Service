import asyncio
import logging
import os # <--- ADD THIS IMPORT
from core.config import settings # <--- KEEP THIS IMPORT
from worker.consumer import RiskCalculationConsumer

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting Risk Calculation Service...")

    # --- TEMPORARY DIAGNOSTIC CODE ---
    env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    logger.info(f"Checking for .env file at: {env_file_path}")
    if os.path.exists(env_file_path):
        logger.info(".env file found!")
        with open(env_file_path, 'r') as f:
            content = f.read()
            logger.info(f".env file content:\n{content}")
    else:
        logger.error(".env file NOT found at expected location!")
    # --- END TEMPORARY DIAGNOSTIC CODE ---

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