# trading_bot/api_client.py

import ccxt
import pandas as pd
from logger import log
from config import config
import time

class APIClient:
    def __init__(self):
        self.exchange = None
        try:
            exchange_class = getattr(ccxt, 'coinbase')
            self.exchange = exchange_class({
                'apiKey': config.API_KEY,
                'secret': config.API_SECRET,
            })
            log.info(f"Cliente de API de {self.exchange.name} inicializado.")
        except Exception as e:
            log.error(f"Error al inicializar el cliente de la API: {e}")

    def get_historical_data(self, symbol, timeframe, limit=400):
        # ... (Esta función no necesita cambios, la dejo por completitud)
        if not self.exchange or not self.exchange.has['fetchOHLCV']:
            log.error("El cliente del exchange no está inicializado.")
            return None
        try:
            log.info(f"Obteniendo datos históricos para {symbol} (hasta {limit} velas)...")
            all_ohlcv = []
            since = None
            fetch_limit = 300
            while len(all_ohlcv) < limit:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=fetch_limit)
                if not ohlcv: break
                since = ohlcv[0][0] - 1
                all_ohlcv = ohlcv + all_ohlcv
                time.sleep(self.exchange.rateLimit / 1000)
            df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.tail(limit)
            log.info(f"Datos históricos para {symbol} obtenidos y procesados ({len(df)} velas).")
            return df
        except Exception as e:
            log.error(f"Error al obtener datos históricos para {symbol}: {e}")
            return None

    def get_balance(self, currency):
        # ... (Esta función no necesita cambios) ...
        if not self.exchange:
            log.error("El cliente del exchange no está inicializado.")
            return 0.0
        try:
            balance = self.exchange.fetch_balance()
            if currency in balance and 'free' in balance[currency]:
                return float(balance[currency]['free'])
            return 0.0
        except Exception as e:
            log.error(f"Error al obtener el balance para {currency}: {e}")
            return None

api_client = APIClient()