import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import json
import os
from pathlib import Path

def train_and_save_model():
    print("Démarrage de l'entraînement du modèle IA (Random Forest)...")
    
    # 1. Chargement des données
    data_path = Path('data/processed/historical_dwell_times.csv')
    if not data_path.exists():
        print("Erreur : Fichier de données introuvable.")
        return
        
    df = pd.read_csv(data_path)
    
    # 2. Préparation des données (Preprocessing)
    X = df[['size', 'weight', 'type', 'specialty', 'arrival_day_of_week', 'arrival_month']]
    y = df['dwell_time_days']
    
    # Encodage One-Hot
    X_encoded = pd.get_dummies(X, columns=['type', 'specialty'])
    
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
    
    # 3. Entraînement
    print("Entraînement en cours (cela peut prendre quelques secondes)...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    # 4. Évaluation
    y_pred = rf_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Performance - MAE: {mae:.2f} jours | RMSE: {rmse:.2f} jours")
    
    # 5. Sauvegarde
    app_dir = Path('app')
    os.makedirs(app_dir, exist_ok=True)
    
    model_path = app_dir / 'marsa_dwell_time_model.joblib'
    joblib.dump(rf_model, model_path)
    
    columns_path = app_dir / 'model_columns.json'
    with open(columns_path, 'w') as f:
        json.dump(list(X_encoded.columns), f)
        
    print(f"Modèle sauvegardé avec succès dans : {model_path}")

if __name__ == "__main__":
    train_and_save_model()
