"""
ai_logic.py - Modele de prediction du True Departure Time (TDT)
Marsa Maroc PFE - Machine Learning avec Random Forest

Ce module predit la date de sortie reelle d'un conteneur
a partir de ses caracteristiques, car les dates BAPLIE sont souvent
imprécises (+/- quelques heures voire jours).
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from datetime import datetime, timedelta

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

MODEL_PATH = Path(__file__).parent.parent / "data" / "models" / "tdt_model.pkl"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


class TDTPredictor:
    """
    Predicteur du True Departure Time (TDT).
    Corrige les dates theoriques BAPLIE par des predictions ML.
    """

    def __init__(self):
        self.model = None
        self.encoders = {}
        self.feature_cols = ["dimension", "categorie", "poids_kg", "scheduled_hour", "scheduled_dow"]
        self.is_trained = False

    def _encode_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Encode les variables categoriques."""
        df = df.copy()
        for col in ["dimension", "categorie"]:
            if col in df.columns:
                if fit:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.encoders[col] = le
                else:
                    if col in self.encoders:
                        df[col] = self.encoders[col].transform(df[col].astype(str))
        return df

    def _build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Construit les features a partir des donnees brutes."""
        df = df.copy()
        if "departure_time" in df.columns:
            dt = pd.to_datetime(df["departure_time"], errors="coerce")
            df["scheduled_hour"] = dt.dt.hour
            df["scheduled_dow"] = dt.dt.dayofweek
        return df

    def train(self, df: pd.DataFrame, target_col: str = "real_departure_hours_delta") -> dict:
        """
        Entraine le modele Random Forest.

        Args:
            df: DataFrame avec colonnes [dimension, categorie, poids_kg,
                departure_time, real_departure_hours_delta]
            target_col: colonne cible = ecart en heures entre BAPLIE et reel

        Returns:
            dict avec metriques (MAE, R2)
        """
        df = self._build_features(df)
        df = self._encode_features(df, fit=True)

        # Si la colonne cible n'existe pas, on la genere synthetiquement
        if target_col not in df.columns:
            print("[AI] Colonne cible absente - generation de donnees synthetiques...")
            np.random.seed(42)
            df[target_col] = np.random.normal(loc=2.0, scale=8.0, size=len(df))

        X = df[self.feature_cols].fillna(0)
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Metriques
        y_pred = self.model.predict(X_test)
        metrics = {
            "mae_hours": round(float(mean_absolute_error(y_test, y_pred)), 2),
            "r2_score": round(float(r2_score(y_test, y_pred)), 4),
            "samples": len(df),
            "features": self.feature_cols,
        }

        print(f"[AI] Modele entraine | MAE={metrics['mae_hours']}h | R2={metrics['r2_score']}")
        return metrics

    def predict_tdt(self, container: dict) -> dict:
        """
        Predit le True Departure Time d'un conteneur.

        Args:
            container: dict avec {dimension, categorie, poids_kg, departure_time}

        Returns:
            dict avec departure_time_predicted (datetime), delta_hours (float)
        """
        if not self.is_trained:
            # Mode sans modele: retourne la date theorique +/- bruit faible
            planned_dt = pd.to_datetime(container.get("departure_time", datetime.now()))
            return {
                "departure_time_predicted": planned_dt.isoformat(),
                "delta_hours": 0.0,
                "confidence": "low - modele non entraine",
            }

        row = pd.DataFrame([{
            "dimension": container.get("dimension", "20"),
            "categorie": container.get("categorie", "import"),
            "poids_kg": float(container.get("weight", 20000)),
            "departure_time": container.get("departure_time", datetime.now()),
        }])

        row = self._build_features(row)
        row = self._encode_features(row, fit=False)
        X = row[self.feature_cols].fillna(0)

        delta_hours = float(self.model.predict(X)[0])
        planned_dt = pd.to_datetime(container.get("departure_time", datetime.now()))
        predicted_dt = planned_dt + timedelta(hours=delta_hours)

        return {
            "departure_time_predicted": predicted_dt.isoformat(),
            "delta_hours": round(delta_hours, 2),
            "confidence": "high" if abs(delta_hours) < 12 else "medium",
        }

    def save(self, path: Path = MODEL_PATH) -> None:
        """Sauvegarde le modele entrainé en .pkl."""
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "encoders": self.encoders}, f)
        print(f"[AI] Modele sauvegarde dans {path}")

    def load(self, path: Path = MODEL_PATH) -> bool:
        """Charge un modele sauvegarde."""
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.encoders = data["encoders"]
            self.is_trained = True
            print(f"[AI] Modele charge depuis {path}")
            return True
        except FileNotFoundError:
            print("[AI] Aucun modele sauvegarde trouve.")
            return False


# Instance globale (singleton) pour eviter de recharger a chaque requete
_predictor_instance: TDTPredictor | None = None


def get_predictor() -> TDTPredictor:
    """Retourne l'instance singleton du predicteur (charge ou entraine)."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = TDTPredictor()
        loaded = _predictor_instance.load()
        if not loaded:
            print("[AI] Modele absent - utilisation en mode degradé.")
    return _predictor_instance


if __name__ == "__main__":
    # Test rapide d'entrainement avec donnees synthetiques
    from data_loader import YardManager

    print("=== Test Entrainement TDT Predictor ===")
    loader = YardManager()
    loader.load_data()

    predictor = TDTPredictor()
    metrics = predictor.train(loader.df_arrivals)
    print("Metriques :", metrics)

    predictor.save()

    # Test de prediction
    test_container = {
        "dimension": "40",
        "categorie": "export",
        "weight": 28000,
        "departure_time": "2026-04-25 14:00:00",
    }
    prediction = predictor.predict_tdt(test_container)
    print("Prediction TDT :", prediction)
