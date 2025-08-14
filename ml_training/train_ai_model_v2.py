# ml_training/train_ai_model_v2.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE # <-- Importamos SMOTE
import joblib

def train_smarter_model(data_path='ai_training_data.csv'):
    """
    Carga los datos, los equilibra con SMOTE, entrena un modelo y lo guarda.
    """
    print("Iniciando el proceso de entrenamiento del modelo v2 con SMOTE...")

    # 1. Cargar los datos
    try:
        df = pd.read_csv(data_path, index_col='timestamp')
        df.dropna(inplace=True)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de datos '{data_path}'.")
        return

    X = df.drop('label', axis=1)
    y = df['label']

    # 2. Dividir en conjunto de entrenamiento y de prueba ANTES de aplicar SMOTE
    # Es crucial que el conjunto de prueba siga representando el mundo real (desbalanceado).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Datos divididos: {len(X_train)} para entrenamiento, {len(X_test)} para prueba.")
    print(f"Distribución original en entrenamiento:\n{y_train.value_counts(normalize=True)}")

    # 3. Aplicar SMOTE solo al conjunto de entrenamiento
    print("\nEquilibrando el conjunto de entrenamiento con SMOTE...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"Nueva distribución en entrenamiento:\n{y_train_resampled.value_counts(normalize=True)}")

    # 4. Entrenar el modelo con los datos equilibrados
    print("\nEntrenando el modelo RandomForest con datos equilibrados...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_resampled, y_train_resampled)
    print("Modelo v2 entrenado exitosamente.")

    # 5. Evaluar el modelo en el conjunto de prueba original (desbalanceado)
    print("\n--- Evaluación del Modelo v2 en el Conjunto de Prueba ---")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Precisión (Accuracy): {accuracy:.2%}") # ¡Espera que este número sea más bajo!
    
    print("\nReporte de Clasificación v2:")
    print(classification_report(y_test, y_pred))

    # 6. Guardar el nuevo modelo
    model_filename = 'ai_model_v2.joblib'
    joblib.dump(model, model_filename)
    print(f"\nModelo v2 guardado exitosamente como '{model_filename}'")


if __name__ == "__main__":
    train_smarter_model()