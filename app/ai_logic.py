import pandas as pd
from datetime import datetime, timedelta
import pickle
import json
from pathlib import Path

class DeparturePredictor:
    """
    Modèle de Machine Learning (Random Forest) entraîné pour prédire 
    la date de départ (TDT - True Departure Time) des conteneurs.
    """
    def __init__(self):
        self.model = None
        self.scaler = None
        self.columns = None
        self.is_trained = False
        self.load_model()

    def load_model(self):
        """Charge le modèle ML entraîné et le Scaler (Normalisation) depuis le disque."""
        model_path = Path(__file__).parent.parent / 'data' / 'models' / 'marsa_dwell_time_model.pkl'
        scaler_path = Path(__file__).parent.parent / 'data' / 'models' / 'marsa_scaler.pkl'
        cols_path = Path(__file__).parent.parent / 'data' / 'models' / 'model_columns.json'
        
        if model_path.exists() and cols_path.exists() and scaler_path.exists():
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                with open(cols_path, 'r') as f:
                    self.columns = json.load(f)
                self.is_trained = True
                print("[IA] Pipeline ML (Modèle + Scaler) chargée avec succès depuis data/models/")
            except Exception as e:
                print(f"[IA] Erreur lors du chargement de la pipeline ML : {e}")
        else:
            print(f"[IA] Attention : Modèle ou Scaler non trouvé dans {model_path.parent}. Mode simulation activé.")

    def predict_tdt(self, container_data):
        """
        Prédit la date de départ via l'inférence du modèle Random Forest.
        """
        container_type = str(container_data.get('type_conteneur', 'IMPORT')).upper()
        weight = float(container_data.get('weight', 15.0))
        size = float(container_data.get('size', 20.0))
        specialty = str(container_data.get('special_type', 'NORMAL')).upper()
        
        if self.is_trained and self.model and self.columns:
            # 1. Construction du vecteur de features (Data Preparation)
            input_dict = {
                'size': size,
                'weight': weight,
                'arrival_day_of_week': datetime.now().weekday(),
                'arrival_month': datetime.now().month
            }
            df_input = pd.DataFrame([input_dict])
            
            # 2. Encodage One-Hot dynamique pour coller au modèle entraîné
            for col in self.columns:
                if col.startswith('type_'):
                    expected_type = col.split('type_')[1]
                    df_input[col] = 1 if container_type == expected_type else 0
                elif col.startswith('specialty_'):
                    expected_spec = col.split('specialty_')[1]
                    df_input[col] = 1 if specialty == expected_spec else 0
                elif col not in df_input.columns:
                    df_input[col] = 0
                    
            # 3. Normalisation (Scaling) et Inférence ML
            # On utilise le scaler entraîné pour transformer la nouvelle donnée
            X_scaled = self.scaler.transform(df_input)
            predicted_days = float(self.model.predict(X_scaled)[0])
            confidence = "Très Haute (XGBoost Scaled Inference)"
            model_name = "Master_XGBoost_Marsa"
        else:
            # Fallback basique si le fichier n'est pas là
            predicted_days = 4.0
            if 'FRIGO' in specialty: predicted_days = 2.0
            if 'DANGER' in specialty: predicted_days = 3.0
            if weight > 25: predicted_days += 1.0
            confidence = "Basse (Règles Expertes de Secours)"
            model_name = "Simulateur_Heuristique"

        # Sécurité : Un conteneur reste au moins 12h (0.5 jour)
        predicted_days = max(0.5, predicted_days)
        predicted_date = datetime.now() + timedelta(days=predicted_days)
        
        return {
            "departure_time_predicted": predicted_date.isoformat(),
            "dwell_time_days": round(predicted_days, 1),
            "confidence": confidence,
            "model": model_name
        }

def get_predictor():
    return DeparturePredictor()
