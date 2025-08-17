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

    # Credenciales de Telegram para notificaciones
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Modo de operación (LIVE vs. SIMULATED)
    BOT_MODE = os.getenv("BOT_MODE", "SIMULATED")
    
    # Clave de API de Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # --- CORRECCIÓN: EL BLOQUE DE CONFIGURACIÓN DE LA ESTRATEGIA VA AQUÍ DENTRO ---
    STRATEGY_CONFIG = {
        # Parámetros optimizados
        'leverage': 5.0,
        'adx_min': 18.0,
        'kc_mult': 1.8,
        'atr_stop_mult': 2.0,
        
        # Parámetros fijos de la estrategia
        'don_len': 20,
        'kc_len': 20,
        'ema_fast_len': 50,
        'ema_slow_len': 200,
        'adx_len': 14,
        'risk_pct': 0.01, # Arriesgar el 1% del capital por operación
        'tp_r_mult': 1.5,
    }
    # --- FIN DE LA CORRECCIÓN ---

# Crear una instancia de la configuración para ser importada en otros módulos
config = Config()