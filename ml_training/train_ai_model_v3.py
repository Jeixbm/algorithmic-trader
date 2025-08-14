# ml_training/train_ai_model_v3.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib

def train_final_model(data_path='ai_training_data_v2.csv'):
    """
    Carga el dataset avanzado, lo equilibra con SMOTE, y entrena la v3 del modelo.
    """
    print("Iniciando el proceso de entrenamiento del modelo v3 con el dataset avanzado...")

    # 1. Cargar el nuevo dataset
    try:
        df = pd.read_csv(data_path, index_col='timestamp')
        df.dropna(inplace=True)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de datos '{data_path}'.")
        print("Asegúrate de haber ejecutado 'prepare_ai_data_v2.py' primero.")
        return

    print(f"Dataset v2 cargado con {len(df)} muestras.")
    print(f"Distribución de clases:\n{df['label'].value_counts(normalize=True)}")

    # 2. Separar Features (X) y Target (y)
    X = df.drop('label', axis=1)
    y = df['label']

    # 3. Dividir en conjunto de entrenamiento y de prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Aplicar SMOTE al conjunto de entrenamiento
    print("\nEquilibrando el conjunto de entrenamiento con SMOTE...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"Nueva distribución en entrenamiento equilibrada.")

    # 5. Entrenar el modelo
    print("\nEntrenando el modelo RandomForest con el dataset avanzado...")
    model = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=10, min_samples_leaf=5)
    model.fit(X_train_resampled, y_train_resampled)
    print("Modelo v3 entrenado exitosamente.")

    # 6. Evaluar el modelo
    print("\n--- Evaluación del Modelo v3 en el Conjunto de Prueba ---")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Precisión (Accuracy): {accuracy:.2%}")
    
    print("\nReporte de Clasificación v3:")
    print(classification_report(y_test, y_pred))

    # 7. Guardar el modelo final
    model_filename = 'ai_model_v3.joblib'
    joblib.dump(model, model_filename)
    print(f"\nModelo v3 guardado exitosamente como '{model_filename}'")

if __name__ == "__main__":
    train_final_model()