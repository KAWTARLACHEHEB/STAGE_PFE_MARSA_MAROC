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
            if pd.isna(row['zone']) or pd.isna(row['niveau_z']):
                continue

            key = f"{row['zone']}-{row['allee']}-{row['pile']}"
            self.yard_state.setdefault(key, []).append(
                {
                    "id": row["reference"],
                    "z": int(row["niveau_z"]),
                    "departure": row["departure_time"],
                    "weight": row.get("weight", 20000),
                    "flux": row.get("flux", "IMPORT"),
                    "statut_import": row.get("statut_import"),
                    "navire_id": row.get("navire_id"),
                    "pod": row.get("pod"),
                    "special_type": row.get("specialite", "NORMAL"),
                }
            )

        for key in self.yard_state:
            self.yard_state[key].sort(key=lambda x: x["z"])

        print(f"[DataLoader] Yard map: {len(self.yard_state)} piles actives.")

    def add_container(self, container_dict, slot_string, terminal):
        """
        Ajoute un conteneur au parc en temps reel (Digital Twin).
        slot_string est au format : ZONE-ALLEE-PILE-Niveau (ex: AE-1-A-N01)
        """
        try:
            parts = slot_string.split('-')
            if len(parts) >= 4:
                zone = parts[0]
                allee = parts[1]
                pile = parts[2]
                niveau = int(parts[3].replace('N', ''))
                
                key = f"{zone}-{allee}-{pile}"
                new_c = {
                    "id": container_dict.get("reference"),
                    "z": niveau,
                    "departure": container_dict.get("departure_time"),
                    "weight": container_dict.get("weight", 20000),
                    "flux": container_dict.get("flux", "IMPORT"),
                    "statut_import": container_dict.get("statut_import"),
                    "navire_id": container_dict.get("navire_id"),
                    "pod": container_dict.get("pod"),
                    "special_type": container_dict.get("special_type", "NORMAL"),
                }
                
                if key not in self.yard_state:
                    self.yard_state[key] = []
                self.yard_state[key].append(new_c)
                self.yard_state[key].sort(key=lambda x: x["z"])
                print(f"[DataLoader] Conteneur {new_c['id']} ajoute virtuellement en {key} (Niv {niveau})")
        except Exception as e:
            print(f"[DataLoader] Erreur ajout virtuel: {e}")

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
