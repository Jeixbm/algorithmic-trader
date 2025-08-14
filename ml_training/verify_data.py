# ml_training/verify_data.py
import pandas as pd

def verify_dataset(filename='BTC_USDT_4h_data.csv'):
    """
    Analiza un archivo de datos históricos y genera un reporte de integridad.
    """
    print(f"\n--- Verificando la integridad del archivo: {filename} ---")
    
    try:
        # Cargar el dataset, asegurándose de que la primera columna sea el índice de fechas
        df = pd.read_csv(filename, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{filename}'.")
        return
        
    # --- 1. Verificación del Periodo de Tiempo ---
    start_date = df.index.min()
    end_date = df.index.max()
    duration = end_date - start_date
    
    print("\n✅ 1. Análisis del Periodo de Tiempo:")
    print(f"   - Fecha de inicio: {start_date.date()}")
    print(f"   - Fecha de fin:    {end_date.date()}")
    print(f"   - Duración total:  {duration.days} días (aprox. {duration.days / 365.25:.2f} años)")

    # --- 2. Verificación de Duplicados ---
    total_rows = len(df)
    unique_rows = len(df.index.unique())
    
    print("\n✅ 2. Análisis de Duplicados:")
    print(f"   - Filas totales:    {total_rows}")
    print(f"   - Fechas únicas:    {unique_rows}")
    
    if total_rows == unique_rows:
        print("   - Resultado: ¡Excelente! No se encontraron datos duplicados.")
    else:
        print(f"   - ❌ ADVERTENCIA: Se encontraron {total_rows - unique_rows} filas duplicadas.")

    print("\n----------------------------------------------------")

if __name__ == "__main__":
    verify_dataset(filename='BTC_USDT_4h_data.csv')