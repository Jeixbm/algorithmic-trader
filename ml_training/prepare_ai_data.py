# ml_training/prepare_ai_data.py

import sys
import os
# --- INICIO DE LA CORRECCIÓN ---
# Añade la carpeta superior (el directorio principal del proyecto) al path de Python.
# Esto permite que Python encuentre los archivos como strategy.py.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- FIN DE LA CORRECCIÓN ---

import pandas as pd
import numpy as np
import pandas_ta as ta
# --- CORRECCIÓN CLAVE ---
# Ahora importamos 'strategy' directamente, sin 'trading_bot.'
from strategy import Strategy 

def generate_historical_data(years=3):
    """Genera un historial de precios de BTC para el entrenamiento."""
    periods = years * 365 * 6
    print(f"Generando {periods:,} velas de datos históricos ({years} años)...")
    precios = 40000 + np.random.randn(periods).cumsum() * 50
    for _ in range(years * 2):
        start = np.random.randint(0, periods - 100)
        end = start + np.random.randint(50, 100)
        factor = np.random.uniform(0.85, 1.15)
        precios[start:end] *= factor
    fechas = pd.to_datetime(pd.date_range(end='2025-08-12', periods=periods, freq='4h'))
    df = pd.DataFrame(precios, index=fechas, columns=['close'])
    df['open'] = df['close'].shift(1)
    df['high'] = df[['open', 'close']].max(axis=1) + np.random.uniform(0, 100, periods)
    df['low'] = df[['open', 'close']].min(axis=1) - np.random.uniform(0, 100, periods)
    df['volume'] = 100 + np.random.randint(0, 50, periods)
    df.dropna(inplace=True)
    return df

def create_features_and_labels(historical_data, strategy):
    """
    Encuentra señales, crea features y etiqueta los resultados para crear un dataset de entrenamiento.
    """
    print("Calculando indicadores para todo el dataset...")
    historical_data.ta.ema(length=strategy.btc_ema_fast_period, append=True)
    historical_data.ta.ema(length=strategy.btc_ema_slow_period, append=True)
    historical_data.ta.rsi(append=True)
    historical_data.ta.atr(append=True)
    historical_data['volume_sma'] = historical_data['volume'].rolling(window=20).mean()

    historical_data.rename(columns={
        f'EMA_{strategy.btc_ema_fast_period}': 'EMA_fast',
        f'EMA_{strategy.btc_ema_slow_period}': 'EMA_slow'
    }, inplace=True)

    signals = []
    print("Buscando señales de compra de la estrategia original...")
    for i in range(strategy.btc_ema_slow_period, len(historical_data)):
        data_slice = historical_data.iloc[i-1:i]
        latest_data = data_slice.iloc[-1]
        
        is_uptrend = latest_data['EMA_fast'] > latest_data['EMA_slow']
        price_touched_ema_fast = latest_data['low'] <= latest_data['EMA_fast']

        if is_uptrend and price_touched_ema_fast:
            features = {
                'timestamp': latest_data.name,
                'RSI': latest_data['RSI_14'],
                'ATR': latest_data['ATRr_14'],
                'VOL_RATIO': latest_data['volume'] / latest_data['volume_sma']
            }

            take_profit_price = latest_data['close'] * 1.05
            stop_loss_price = latest_data['close'] * 0.97
            
            future_data = historical_data.iloc[i:i+10]
            price_hit_tp = (future_data['high'] >= take_profit_price).any()
            price_hit_sl = (future_data['low'] <= stop_loss_price).any()

            label = 0
            if price_hit_tp and not price_hit_sl:
                label = 1
            
            features['label'] = label
            signals.append(features)
    
    print(f"Se encontraron y etiquetaron {len(signals)} señales.")
    return pd.DataFrame(signals)

if __name__ == "__main__":
    btc_strategy = Strategy()
    data = generate_historical_data(years=3)
    ai_dataset = create_features_and_labels(data, btc_strategy)
    
    if not ai_dataset.empty:
        ai_dataset.set_index('timestamp', inplace=True)
        output_file = 'ai_training_data.csv'
        ai_dataset.to_csv(output_file)
        print(f"\nDataset para IA creado y guardado como '{output_file}'")
        print("Primeras 5 filas del dataset:")
        print(ai_dataset.head())
    else:
        print("No se generaron suficientes señales para crear un dataset.")