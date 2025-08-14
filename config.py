# config.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """
    Clase de configuración para cargar y gestionar las variables de entorno
    y otros parámetros de configuración del bot.
    """
    # Credenciales del Exchange
    API_KEY = os.getenv("EXCHANGE_API_KEY")
    API_SECRET = os.getenv("EXCHANGE_API_SECRET")

    # --- NUEVAS LÍNEAS ---
    # Credenciales de Telegram para notificaciones
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    # --- FIN DE NUEVAS LÍNEAS ---

    # Modo de operación (LIVE vs. SIMULATED)
    BOT_MODE = os.getenv("BOT_MODE", "SIMULATED")

# Crear una instancia de la configuración para ser importada en otros módulos
config = Config()