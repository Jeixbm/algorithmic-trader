# logger.py
import logging
import sys

def setup_logger():
    """
    Configura un logger para registrar eventos en la consola y en un archivo.
    """
    # Crear un logger
    logger = logging.getLogger("TradingBot")
    logger.setLevel(logging.INFO)

    # Evitar que los logs se propaguen al logger raíz
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formateador para los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para escribir en un archivo (bot_logs.log)
    file_handler = logging.FileHandler("bot_logs.log")
    file_handler.setFormatter(formatter)

    # Handler para mostrar logs en la consola
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Añadir handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

# Crear una instancia del logger para ser importada en otros módulos
log = setup_logger()