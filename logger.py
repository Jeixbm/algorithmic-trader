# logger.py
import logging
import sys

def setup_logger():
    """
    Configura un logger para registrar eventos en la consola y en un archivo,
    asegurando la codificación UTF-8 para soportar todos los caracteres.
    """
    logger = logging.getLogger("TradingBot")
    logger.setLevel(logging.INFO) # Nivel por defecto

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Para el archivo de logs
    file_handler = logging.FileHandler("bot_logs.log", encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Para la salida en la consola
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

log = setup_logger()

# --- NUEVA FUNCIÓN AÑADIDA ---
def set_log_level(level):
    """
    Permite cambiar el nivel del logger dinámicamente.
    Niveles comunes: 'INFO', 'WARNING', 'ERROR'
    """
    log.setLevel(getattr(logging, level.upper(), logging.INFO))