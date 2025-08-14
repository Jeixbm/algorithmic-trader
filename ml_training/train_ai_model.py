# ml_training/train_ai_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

def train_model(data_path='ai_training_data.csv'):
    """
    Carga los datos, entrena un modelo de clasificación y guarda el resultado.
    """
    print("Iniciando el proceso de entrenamiento del modelo de IA...")

    # 1. Cargar los datos
    try:
        df = pd.read_csv(data_path, index_col='timestamp')
        df.dropna(inplace=True) # Eliminar filas con posibles valores nulos
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de datos '{data_path}'.")
        print("Por favor, ejecuta primero 'prepare_ai_data.py'.")
        return

    if 'label' not in df.columns:
        print("Error: El dataset no contiene la columna 'label'.")
        return
    
    print(f"Dataset cargado con {len(df)} muestras.")
    print(f"Distribución de clases:\n{df['label'].value_counts(normalize=True)}")

    # 2. Separar Features (X) y Target (y)
    X = df.drop('label', axis=1)
    y = df['label']

    # 3. Dividir en conjunto de entrenamiento y de prueba (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Datos divididos: {len(X_train)} para entrenamiento, {len(X_test)} para prueba.")

    # 4. Entrenar el modelo RandomForest
    print("\nEntrenando el modelo RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    print("Modelo entrenado exitosamente.")

    # 5. Evaluar el modelo
    print("\n--- Evaluación del Modelo en el Conjunto de Prueba ---")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Precisión (Accuracy): {accuracy:.2%}")
    
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, y_pred))

    # 6. Guardar el modelo entrenado
    model_filename = 'ai_model.joblib'
    joblib.dump(model, model_filename)
    print(f"\nModelo guardado exitosamente como '{model_filename}'")


if __name__ == "__main__":
    train_model()