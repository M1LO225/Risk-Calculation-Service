import os
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging # Añadir logging aquí también

logger = logging.getLogger(__name__)

# Configura el logger para que imprima mensajes informativos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- INICIO CÓDIGO DE DEPURACIÓN CRÍTICO ---
# Intentamos determinar la ruta del .env antes de que pydantic-settings lo haga.
# Esto se ejecuta en el momento de la importación del módulo.
current_dir = os.path.dirname(os.path.abspath(__file__))
# The .env file should be in the parent directory of core/config.py
# if core/config.py is in a 'core' subdirectory.
# But based on your path "c:\Users\Usuario\Desktop\Risk Calculation Service\core\config.py",
# the .env should be in "c:\Users\Usuario\Desktop\Risk Calculation Service\"
# So, the path is correct assuming core/config.py is inside 'core' and .env is at root.

# Let's adjust the path if 'core' is a subdirectory and .env is at the service root
# If core/config.py is at: .../Risk Calculation Service/core/config.py
# And .env is at:       .../Risk Calculation Service/.env
# Then we need to go up one level from current_dir
env_file_path_expected = os.path.join(os.path.dirname(current_dir), ".env") 

logger.info(f"[DEBUG_CONFIG] Intentando cargar configuración. Buscando .env en: {env_file_path_expected}")

if not os.path.exists(env_file_path_expected):
    logger.error(f"[DEBUG_CONFIG] ¡ERROR! El archivo .env NO SE ENCUENTRA en la ruta esperada: {env_file_path_expected}")
    logger.error("[DEBUG_CONFIG] Asegúrate de que .env está en la carpeta raíz del servicio (Risk Calculation Service).")
else:
    logger.info(f"[DEBUG_CONFIG] Archivo .env ENCONTRADO en: {env_file_path_expected}")
    try:
        with open(env_file_path_expected, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"[DEBUG_CONFIG] Contenido de .env:\n--- START .ENV CONTENT ---\n{content}\n--- END .ENV CONTENT ---")
    except Exception as e:
        logger.error(f"[DEBUG_CONFIG] Error al leer el archivo .env: {e}")
# --- FIN CÓDIGO DE DEPURACIÓN CRÍTICO ---


class Settings(BaseSettings):
    # Temporarily change to just this one variable to isolate the issue
    TEST_VAR: str 

    # Specify the path relative to the *current working directory* of the script execution (main.py)
    # Or, relative to this config file's location if you use it like env_file_path_expected
    # For simplicity, if .env is at service root, and core/config.py is in 'core' sub-dir,
    # you might need to specify the path to .env explicitly for pydantic_settings.
    # Let's keep it ".env" as it implies CWD, which should be 'Risk Calculation Service' folder when main.py runs.
    model_config = SettingsConfigDict(env_file=env_file_path_expected, extra="ignore") # Use the absolute path found above

try:
    settings = Settings()
    logger.info(f"[DEBUG_CONFIG] ¡Configuración cargada con éxito! TEST_VAR: {settings.TEST_VAR}")
except Exception as e:
    logger.critical(f"[DEBUG_CONFIG] ¡ERROR CRÍTICO! Falló la inicialización de Settings: {e}", exc_info=True)
    raise # Re-raise to make the program fail as before