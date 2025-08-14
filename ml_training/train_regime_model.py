# ml_training/train_regime_model.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import pandas_ta as ta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

def create_regime_labels(data):
    """
    Analiza datos históricos y etiqueta cada vela con un régimen de mercado.
    """
    print("Etiquetando datos con regímenes de mercado...")
    
    # Calcular indicadores para definir los regímenes
    data.ta.ema(length=50, append=True)
    data.ta.ema(length=200, append=True)
    data.ta.adx(append=True) # ADX mide la fuerza de la tendencia

    # Definir las condiciones para cada régimen
    # Régimen 1: Tendencia Alcista Fuerte
    cond_bull = (data['EMA_50'] > data['EMA_200']) & (data['ADX_14'] > 25)
    # Régimen -1: Tendencia Bajista Fuerte
    cond_bear = (data['EMA_50'] < data['EMA_200']) & (data['ADX_14'] > 25)
    # Régimen 0: Mercado Lateral o sin tendencia clara
    # (Cualquier cosa que no sea una tendencia fuerte)
    
    # Asignar etiquetas
    data['regime'] = 0 # Por defecto es lateral
    data.loc[cond_bull, 'regime'] = 1
    data.loc[cond_bear, 'regime'] = -1
    
    print("Distribución de regímenes:")
    print(data['regime'].value_counts(normalize=True))
    return data

def train_regime_model(data_path='btc_1d_historical_data.csv'):
    """
    Entrena un modelo de IA para clasificar el régimen de mercado.
    """
    print(f"\nIniciando entrenamiento del modelo de detección de régimen...")
    try:
        df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de datos '{data_path}'.")
        return

    df = create_regime_labels(df)
    
    # --- Crear Features ---
    # Usaremos indicadores de momentum y volatilidad como "pistas" para el modelo
    df.ta.rsi(append=True)
    df.ta.atr(append=True)
    df.ta.macd(append=True)
    df.dropna(inplace=True)

    features = ['RSI_14', 'ATRr_14', 'MACDh_12_26_9']
    target = 'regime'
    
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("\nEntrenando el modelo RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    print("Modelo de régimen entrenado exitosamente.")

    print("\n--- Evaluación del Modelo de Régimen ---")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    model_filename = 'market_regime_model.joblib'
    joblib.dump(model, model_filename)
    print(f"\nModelo de régimen guardado como '{model_filename}'")


if __name__ == "__main__":
    train_regime_model()