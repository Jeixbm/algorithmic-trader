# health_checker.py
from config import config
from api_client import api_client
from logger import log

def perform_initial_checks():
    """
    Realiza una serie de verificaciones iniciales para asegurar que el bot
    puede arrancar de forma segura.
    """
    log.info("Iniciando diagnósticos de salud del sistema...")
    
    # 1. Verificar que las credenciales están presentes en la configuración
    log.info("Verificando la presencia de credenciales...")
    if not config.API_KEY or not config.API_SECRET:
        log.critical("Error Crítico: Las claves de API no están definidas en el archivo .env. El bot no puede continuar.")
        return False
    log.info("Credenciales encontradas.")

    # 2. Verificar la conexión a la API del exchange
    log.info("Verificando la conexión a la API...")
    if not api_client.check_connection():
        log.critical("Error Crítico: No se pudo establecer conexión con la API del exchange. El bot no puede continuar.")
        return False
    log.info("Diagnóstico de conexión a la API completado con éxito.")
    
    log.info("Todos los diagnósticos iniciales han sido superados. El sistema está operativo.")
    return True