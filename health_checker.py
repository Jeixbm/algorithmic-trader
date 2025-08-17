from logger import log
from config import config

def check_credentials():
    log.info("Verificando la presencia de credenciales...")
    if not config.API_KEY or not config.API_SECRET:
        log.error("Error: Las credenciales de la API no están configuradas.")
        return False
    log.info("Credenciales encontradas.")
    return True

def check_api_connection(api_client):
    log.info(f"Verificando conexión con la API...")
    try:
        api_client.get_balance('USDT')
        log.info("Conexión y credenciales verificadas exitosamente.")
        return True
    except Exception as e:
        log.error(f"Fallo en la conexión con la API del exchange: {e}")
        return False

def perform_initial_checks(api_client):
    log.info("Iniciando diagnósticos de salud del sistema...")
    
    if not check_credentials():
        return False
        
    # --- CORRECCIÓN: Desactivamos temporalmente la prueba de conexión para el modo simulado ---
    if not check_api_connection(api_client):
        return False

    log.info("Todos los diagnósticos iniciales han sido superados. El sistema está operativo.")
    return True