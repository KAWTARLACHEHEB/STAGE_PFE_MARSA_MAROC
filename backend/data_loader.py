import pandas as pd
import numpy as np
import time
from datetime import datetime

class YardManager:
    """
    Gère l'état du parc de conteneurs de Marsa Maroc.
    Optimisé pour la vitesse avec Pandas.
    """
    
    def __init__(self, arrivals_path, snapshot_path):
        self.arrivals_path = arrivals_path
        self.snapshot_path = snapshot_path
        self.df_arrivals = None
        self.df_snapshot = None
        self.yard_state = {} # Dictionnaire pour un accès O(1) aux piles

    def load_data(self):
        """Charge les fichiers CSV et prépare les colonnes Datetime."""
        start_time = time.time()
        
        # Lecture optimisée (uniquement les colonnes nécessaires si possible)
        self.df_arrivals = pd.read_csv(self.arrivals_path)
        self.df_snapshot = pd.read_csv(self.snapshot_path)
        
        # Conversion Datetime vectorisée (très rapide)
        if 'departure_time' in self.df_arrivals.columns:
            self.df_arrivals['departure_time'] = pd.to_datetime(self.df_arrivals['departure_time'])
        
        if 'departure_time' in self.df_snapshot.columns:
            self.df_snapshot['departure_time'] = pd.to_datetime(self.df_snapshot['departure_time'])
            
        load_time = time.time() - start_time
        print(f"Donnees chargees en {load_time:.4f} secondes.")
        return load_time

    @staticmethod
    def parse_slot(slot_string):
        """
        Décompose 'C-012-I-01' -> Zone: C, Allée: 012, Pile: I, Niveau: 01
        """
        try:
            parts = slot_string.split('-')
            return {
                'zone':   parts[0],
                'allee':  parts[1],
                'pile':   parts[2],
                'niveau': int(parts[3])
            }
        except (IndexError, ValueError):
            return None

    def get_occupancy_stats(self):
        """
        Calcule le taux d'occupation par Zone.
        Utilise le snapshot actuel.
        """
        if self.df_snapshot is None:
            return {}
            
        # Extraction de la Zone depuis la colonne 'slot'
        self.df_snapshot['zone'] = self.df_snapshot['slot'].str.split('-').str[0]
        
        # Groupement par zone
        stats = self.df_snapshot.groupby('zone').size().to_dict()
        
        # Imaginons des capacités max par zone (A:2000, B:2000, C:1500, D:1500)
        capacities = {'A': 2000, 'B': 2000, 'C': 1500, 'D': 1500}
        
        occupancy = {
            zone: {
                'count': count,
                'rate': round((count / capacities.get(zone, 1000)) * 100, 2)
            }
            for zone, count in stats.items()
        }
        
        return occupancy

    def build_stack_map(self):
        """
        Organise le parc en dictionnaire de piles pour la logique LIFO.
        Clé : (Zone, Allee, Pile) -> Valeur : Liste de conteneurs triés par Niveau
        """
        self.yard_state = {}
        for _, row in self.df_snapshot.iterrows():
            p = self.parse_slot(row['slot'])
            if p:
                stack_key = f"{p['zone']}-{p['allee']}-{p['pile']}"
                if stack_key not in self.yard_state:
                    self.yard_state[stack_key] = []
                
                self.yard_state[stack_key].append({
                    'id': row['container_id'],
                    'z': p['niveau'],
                    'departure': row['departure_time'],
                    'weight': row.get('weight', 20000) # Poids par défaut si absent
                })
        
        # Tri des piles par niveau Z pour respecter LIFO
        for key in self.yard_state:
            self.yard_state[key].sort(key=lambda x: x['z'])
            
        print(f"Map du parc generee : {len(self.yard_state)} piles actives.")

# Exemple d'utilisation rapide
if __name__ == "__main__":
    # Chemins à adapter selon vos fichiers
    loader = YardManager('data/hybrid_arrivals_1k_v2.csv', 'data/hybrid_snapshot_1k_v2.csv')
    
    try:
        loader.load_data()
        loader.build_stack_map()
        stats = loader.get_occupancy_stats()
        print("Taux d'occupation par Zone :", stats)
    except FileNotFoundError:
        print("Fichiers CSV manquants dans le dossier /data")
