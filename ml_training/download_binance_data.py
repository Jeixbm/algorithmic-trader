# ml_training/download_binance_data.py
import ccxt
import pandas as pd
import time

def download_full_history(product_id='BTC/USDT', granularity='4h', years=3):
    """
    Descarga un historial completo de datos desde Binance.US.
    """
    print(f"Iniciando la descarga de {years} años de datos para {product_id} [{granularity}] desde Binance.US...")

    # --- CORRECCIÓN CLAVE: Conectar a binanceus en lugar de binance ---
    exchange = ccxt.binanceus()

    timeframe_in_ms = exchange.parse_timeframe(granularity) * 1000
    now = exchange.milliseconds()
    since = now - (years * 365 * 24 * 60 * 60 * 1000)
    
    all_candles = []

    while since < now:
        try:
            print(f"Descargando lote de datos desde {pd.to_datetime(since, unit='ms')}...")
            candles = exchange.fetch_ohlcv(product_id, timeframe=granularity, since=since, limit=1000)
            
            if len(candles):
                all_candles.extend(candles)
                since = candles[-1][0] + timeframe_in_ms
            else:
                break

            time.sleep(exchange.rateLimit / 1000)

        except Exception as e:
            print(f"Ocurrió un error: {e}. Reintentando en 30 segundos...")
            time.sleep(30)
    
    print(f"\n✅ Descarga completa. Total de velas obtenidas: {len(all_candles)}")

    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[~df.index.duplicated(keep='first')]

    output_file = f"{product_id.replace('/', '_')}_{granularity}_data.csv"
    df.to_csv(output_file)
    print(f"Datos guardados exitosamente en '{output_file}'")

if __name__ == "__main__":
    # Cambia el par y la granularidad para descargar los datos de Solana
    download_full_history(product_id='SOL/USDT', granularity='4h', years=3)