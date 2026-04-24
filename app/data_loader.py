import pandas as pd
import numpy as np
import time
from datetime import datetime
from sqlalchemy import text

class YardManager:
    """
    Gere l'etat du parc de conteneurs de Marsa Maroc via MySQL.
    """

    def __init__(self, db_engine=None):
        self.engine = db_engine
        self.df_arrivals = pd.DataFrame()
        self.df_snapshot = pd.DataFrame()
        self.yard_state = {}

    def load_data(self) -> float:
        """Charge les donnees depuis MySQL."""
        start = time.time()
        if self.engine is None:
            print("[DataLoader] Warning: No DB engine provided.")
            return 0
            
        try:
            with self.engine.connect() as conn:
                # On recupere tous les conteneurs au sol
                query = text("SELECT * FROM conteneurs")
                self.df_snapshot = pd.read_sql(query, conn)
                self.df_arrivals = self.df_snapshot.copy() # Pour simplifier l'IA
                
            if "departure_time" in self.df_snapshot.columns:
                self.df_snapshot["departure_time"] = pd.to_datetime(self.df_snapshot["departure_time"])
                
            elapsed = time.time() - start
            print(f"[DataLoader] Donnees MySQL chargees en {elapsed:.4f}s ({len(self.df_snapshot)} conteneurs)")
            return elapsed
        except Exception as e:
            print(f"[DataLoader] Erreur MySQL: {e}")
            return 0

    def build_stack_map(self) -> None:
        """Organise le parc en dictionnaire de piles."""
        self.yard_state = {}
        if self.df_snapshot.empty:
            return

        for _, row in self.df_snapshot.iterrows():
            # Dans MySQL les colonnes sont : zone, allee, pile, niveau_z
            key = f"{row['zone']}-{row['allee']}-{row['pile']}"
            self.yard_state.setdefault(key, []).append(
                {
                    "id": row["reference"],
                    "z": int(row["niveau_z"]),
                    "departure": row["departure_time"],
                    "weight": row.get("weight", 20000),
                }
            )

        for key in self.yard_state:
            self.yard_state[key].sort(key=lambda x: x["z"])

        print(f"[DataLoader] Yard map: {len(self.yard_state)} piles actives.")

    def get_occupancy_stats(self) -> dict:
        """Utilise les donnees chargees pour les stats (fallback)."""
        if self.df_snapshot.empty:
            return {}
        
        counts = self.df_snapshot.groupby("zone").size().to_dict()
        return {
            zone: {
                "count": count,
                "capacity": 2000,
                "rate": round((count / 2000) * 100, 2),
            }
            for zone, count in counts.items()
        }
