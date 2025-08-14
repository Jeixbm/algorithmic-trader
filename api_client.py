# trading_bot/api_client.py
import pandas as pd
import ccxt
import time
from config import config
from logger import log

class APIClient:
    """
    Versión 2.0: Cliente de API robusto con lógica de reintentos.
    """
    def __init__(self, max_retries=5, initial_delay=1):
        """
        Inicializa el cliente con parámetros para la lógica de reintentos.
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        try:
            self.client = ccxt.coinbase({
                'apiKey': config.API_KEY,
                'secret': config.API_SECRET,
            })
            log.info("Cliente de API de Coinbase (vía CCXT) inicializado.")
        except Exception as e:
            log.critical(f"Error al inicializar el cliente de API CCXT: {e}")
            self.client = None

    def _execute_api_call(self, api_call_function):
        """
        Función interna que envuelve cualquier llamada a la API con la lógica de reintentos.
        """
        delay = self.initial_delay
        for attempt in range(self.max_retries):
            try:
                # Intenta ejecutar la función que se le pasa (ej. fetch_balance)
                return api_call_function()
            except ccxt.NetworkError as e:
                log.warning(f"Error de red en el intento {attempt + 1}/{self.max_retries}: {e}. Reintentando en {delay}s...")
            except ccxt.ExchangeError as e:
                log.warning(f"Error del exchange en el intento {attempt + 1}/{self.max_retries}: {e}. Reintentando en {delay}s...")
            
            time.sleep(delay)
            delay *= 2 # Duplicar el tiempo de espera (retroceso exponencial)
        
        log.error(f"La llamada a la API falló después de {self.max_retries} intentos.")
        return None

    def check_connection(self):
        """Verifica la conexión usando la lógica de reintentos."""
        if not self.client: return False
        log.info("Verificando conexión con la API de Coinbase (vía CCXT)...")
        
        # Le pasamos la función fetch_balance a nuestro ejecutor de llamadas
        response = self._execute_api_call(lambda: self.client.fetch_balance())
        
        if response is not None:
            log.info("Conexión y credenciales verificadas exitosamente.")
            return True
        else:
            log.error("Fallo en la conexión después de varios reintentos.")
            return False

    def get_historical_data(self, product_id, granularity, limit=300, min_candles=200):
        """Obtiene datos históricos usando la lógica de reintentos."""
        if not self.client: return None
        log.info(f"Obteniendo datos históricos para {product_id}...")

        def api_call():
            return self.client.fetch_ohlcv(product_id.replace('-', '/'), timeframe=granularity, limit=limit)

        ohlcv = self._execute_api_call(api_call)
        
        if ohlcv is None:
            log.warning(f"No se pudieron obtener los datos para {product_id} después de varios reintentos.")
            return None

        if len(ohlcv) < min_candles:
            log.warning(f"La API devolvió {len(ohlcv)} velas, menos de las {min_candles} requeridas.")
            return None

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df.sort_index(ascending=True, inplace=True)
        log.info(f"Datos históricos para {product_id} obtenidos y procesados ({len(df)} velas).")
        return df

# Crear una instancia del cliente para ser importada
api_client = APIClient()