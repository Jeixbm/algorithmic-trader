# ml_training/download_binance_data.py

import ccxt
import pandas as pd
import os
from datetime import datetime

# --- Configuración ---
exchange_id = 'binanceus' # Usamos Binance.US como se definió en la arquitectura
symbol_to_timeframes = {
    'SOL/USDT': ['6h'],
    'BTC/USDT': ['6h', '1d']
}
# Fecha de inicio para descargar los datos (formato: YYYY-MM-DD)
# Usamos una fecha lejana para obtener un historial amplio para el backtest
since_date = '2020-01-01T00:00:00Z'

output_dir = 'data' # Carpeta donde se guardarán los datos

# --- Inicialización del Exchange ---
exchange = getattr(ccxt, exchange_id)()

# --- Lógica de Descarga ---

def download_ohlcv(symbol, timeframe, since):
    """
    Descarga los datos OHLCV de un símbolo y temporalidad específicos.
    """
    print(f"Iniciando descarga para {symbol} en temporalidad {timeframe}...")
    
    since_timestamp = exchange.parse8601(since)
    all_ohlcv = []
    
    while True:
        try:
            # Descargamos los datos en lotes (Binance permite hasta 1000 velas por llamada)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since_timestamp, limit=1000)
            if len(ohlcv) == 0:
                break # No hay más datos disponibles
            
            all_ohlcv.extend(ohlcv)
            since_timestamp = ohlcv[-1][0] + 1 # Actualizamos el timestamp para la siguiente llamada
            
            # Imprimimos el progreso
            last_date = datetime.fromtimestamp(ohlcv[-1][0] / 1000)
            print(f"  Datos obtenidos hasta: {last_date.strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            print(f"Ocurrió un error descargando {symbol} ({timeframe}): {e}")
            break
            
    return all_ohlcv

def save_to_csv(symbol, timeframe, ohlcv_data):
    """
    Guarda los datos OHLCV en un archivo CSV.
    """
    if not ohlcv_data:
        print(f"No hay datos para guardar para {symbol} en {timeframe}.")
        return

    # Creamos el directorio si no existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convertimos a DataFrame de Pandas
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Formateamos el nombre del archivo
    safe_symbol = symbol.replace('/', '_')
    filename = f"{safe_symbol}_{timeframe}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Guardamos el archivo
    df.to_csv(filepath, index=False)
    print(f"Datos guardados exitosamente en: {filepath}")
    print("-" * 30)

# --- Bucle Principal ---

if __name__ == '__main__':
    for symbol, timeframes in symbol_to_timeframes.items():
        for tf in timeframes:
            data = download_ohlcv(symbol, tf, since_date)
            save_to_csv(symbol, tf, data)
    
    print("Descarga de todos los datos completada.")