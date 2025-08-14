# ml_training/prepare_ai_data_v2.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import pandas_ta as ta
from strategy import Strategy 

def create_features_and_labels_v2(historical_data, strategy):
    """
    Toma datos históricos reales, encuentra señales, crea features y etiqueta los resultados.
    """
    print("Calculando indicadores base para todo el dataset...")
    historical_data.ta.ema(length=strategy.btc_ema_fast_period, append=True)
    historical_data.ta.ema(length=strategy.btc_ema_slow_period, append=True)
    historical_data.ta.rsi(append=True)
    historical_data.ta.atr(append=True)
    historical_data.ta.macd(append=True)
    historical_data['volume_sma'] = historical_data['volume'].rolling(window=20).mean()

    historical_data.rename(columns={
        f'EMA_{strategy.btc_ema_fast_period}': 'EMA_fast',
        f'EMA_{strategy.btc_ema_slow_period}': 'EMA_slow',
        'MACDh_12_26_9': 'MACD_hist'
    }, inplace=True)

    print("Realizando ingeniería de features avanzadas...")
    historical_data['EMA_FAST_SLOPE'] = historical_data['EMA_fast'].diff(periods=5)
    historical_data['PRICE_VS_EMA_SLOW'] = (historical_data['close'] - historical_data['EMA_slow']) / historical_data['EMA_slow']

    signals = []
    print("Buscando señales y etiquetando datos con la nueva lógica...")
    start_index = strategy.btc_ema_slow_period if strategy.btc_ema_slow_period > 0 else 0
    
    for i in range(start_index, len(historical_data)):
        if i == 0: continue
        data_slice = historical_data.iloc[i-1:i]
        latest_data = data_slice.iloc[-1]
        
        if pd.isna(latest_data['EMA_fast']) or pd.isna(latest_data['EMA_slow']):
            continue

        is_uptrend = latest_data['EMA_fast'] > latest_data['EMA_slow']
        price_touched_ema_fast = latest_data['low'] <= latest_data['EMA_fast']

        if is_uptrend and price_touched_ema_fast:
            features = {
                'timestamp': latest_data.name,
                'RSI': latest_data['RSI_14'],
                'ATR': latest_data['ATRr_14'],
                'VOL_RATIO': latest_data['volume'] / latest_data['volume_sma'],
                'EMA_FAST_SLOPE': latest_data['EMA_FAST_SLOPE'],
                'PRICE_VS_EMA_SLOW': latest_data['PRICE_VS_EMA_SLOW'],
                'MACD_HIST': latest_data['MACD_hist']
            }

            risk_percentage = 0.03
            reward_percentage = risk_percentage * 2
            take_profit_price = latest_data['close'] * (1 + reward_percentage)
            stop_loss_price = latest_data['close'] * (1 - risk_percentage)
            
            future_window = 50
            future_data = historical_data.iloc[i : i + future_window]

            if not future_data.empty:
                tp_hit_time = future_data[future_data['high'] >= take_profit_price].index.min()
                sl_hit_time = future_data[future_data['low'] <= stop_loss_price].index.min()

                label = 0
                if pd.notna(tp_hit_time) and (pd.isna(sl_hit_time) or tp_hit_time < sl_hit_time):
                    label = 1
                
                features['label'] = label
                signals.append(features)
    
    print(f"Se encontraron y etiquetaron {len(signals)} señales.")
    return pd.DataFrame(signals)

if __name__ == "__main__":
    btc_strategy = Strategy()
    
    # --- CAMBIO CLAVE: Cargar los nuevos datos de Binance ---
    data_filename = 'BTC_USDT_4h_data.csv'
    try:
        print(f"Cargando datos históricos reales desde '{data_filename}'...")
        data = pd.read_csv(data_filename, index_col='timestamp', parse_dates=True)
        print("Datos cargados exitosamente.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{data_filename}'.")
        print("Por favor, ejecuta 'download_binance_data.py' primero.")
        sys.exit()
    
    ai_dataset_v2 = create_features_and_labels_v2(data, btc_strategy)
    
    if not ai_dataset_v2.empty:
        ai_dataset_v2.set_index('timestamp', inplace=True)
        # Guardamos en un nuevo archivo para diferenciarlo
        output_file = 'ai_training_data_4h_v3.csv'
        ai_dataset_v2.to_csv(output_file)
        print(f"\nDataset v3 (4h) para IA creado y guardado como '{output_file}'")
        print("Distribución de clases en el nuevo dataset:")
        print(ai_dataset_v2['label'].value_counts(normalize=True))
    else:
        print("No se generaron suficientes señales para crear un dataset.")