# trading_bot/ai_filter.py
import joblib
import pandas as pd
from logger import log

class AIFilter:
    """
    Carga el modelo de IA entrenado y lo usa para filtrar señales de trading.
    """
    def __init__(self, model_path='ai_model.joblib'):
        """
        Inicializa el filtro cargando el modelo desde el archivo.
        """
        try:
            # Importante: El modelo debe estar en la misma carpeta que main.py
            self.model = joblib.load(model_path)
            log.info(f"Filtro de IA inicializado. Modelo '{model_path}' cargado exitosamente.")
        except FileNotFoundError:
            self.model = None
            log.error(f"Error: No se encontró el archivo del modelo de IA en '{model_path}'. El filtro de IA estará desactivado.")
        except Exception as e:
            self.model = None
            log.error(f"Error al cargar el modelo de IA: {e}. El filtro de IA estará desactivado.")

    def get_confidence_prediction(self, features):
        """
        Usa el modelo para predecir si una señal es de alta confianza.
        
        :param features: Un diccionario con los valores de las features para la predicción.
        :return: 1 si la confianza es alta ("GO"), 0 si es baja ("NO-GO").
        """
        if self.model is None:
            log.warning("El modelo de IA no está cargado. Se permite pasar la señal sin filtro.")
            return 1 # Por seguridad, si el modelo falla, no bloqueamos las operaciones.

        try:
            # Convertir el diccionario de features a un DataFrame de una sola fila
            feature_df = pd.DataFrame([features])
            
            # Asegurarse de que el orden de las columnas coincida con el entrenamiento
            feature_df = feature_df[self.model.feature_names_in_]
            
            prediction = self.model.predict(feature_df)
            log.info(f"Predicción del filtro de IA: {'GO' if prediction[0] == 1 else 'NO-GO'}")
            return prediction[0]
        except Exception as e:
            log.error(f"Error durante la predicción de la IA: {e}")
            return 1 # Fallar en modo abierto para no detener el bot