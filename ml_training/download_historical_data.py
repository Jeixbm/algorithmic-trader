# ml_training/download_historical_data.py
import yfinance as yf
import pandas as pd

def download_daily_data(ticker='BTC-USD', years=5):
    """
    Descarga datos históricos DIARIOS desde Yahoo Finance y los guarda en un CSV.
    """
    print(f"Iniciando la descarga de {years} años de datos diarios para {ticker} desde Yahoo Finance...")

    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(years=years)

    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d', auto_adjust=True)

        if data.empty:
            print(f"No se encontraron datos para {ticker}.")
            return

        # --- CORRECCIÓN CLAVE: Renombrar columnas de forma robusta ---
        # Seleccionamos solo las columnas que necesitamos y les asignamos nombres en minúscula directamente.
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        data.columns = ['open', 'high', 'low', 'close', 'volume']
        
        output_file = 'btc_1d_historical_data.csv'
        data.to_csv(output_file)
        
        print(f"\n✅ Descarga completa. Total de velas obtenidas: {len(data)}")
        print(f"Datos guardados exitosamente en '{output_file}'")

    except Exception as e:
        print(f"❌ Ocurrió un error durante la descarga: {e}")

if __name__ == "__main__":
    download_daily_data(ticker='BTC-USD', years=5)