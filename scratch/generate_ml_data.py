import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_training_data(num_samples=50000, output_file='data/processed/historical_dwell_times.csv'):
    print(f"Génération de {num_samples} échantillons pour l'entraînement ML...")
    
    np.random.seed(42)
    
    # Features
    sizes = np.random.choice([20, 40], num_samples, p=[0.4, 0.6])
    weights = []
    types = np.random.choice(['IMPORT', 'EXPORT', 'TRANSSHIPMENT'], num_samples, p=[0.5, 0.3, 0.2])
    specialties = []
    arrival_days_of_week = np.random.randint(0, 7, num_samples) # 0=Lundi, 6=Dimanche
    arrival_months = np.random.randint(1, 13, num_samples)
    
    # Dwell time (Target)
    dwell_times = []
    
    for i in range(num_samples):
        # Poids logiques
        if types[i] == 'EXPORT':
            weight = np.random.uniform(15, 30) # Souvent pleins
        elif types[i] == 'IMPORT':
            weight = np.random.uniform(5, 25)
        else:
            weight = np.random.uniform(2, 30)
        weights.append(round(weight, 1))
        
        # Spécialités
        spec_prob = np.random.random()
        if spec_prob < 0.05: spec = 'FRIGO'
        elif spec_prob < 0.10: spec = 'DANGER'
        elif spec_prob < 0.12: spec = 'OOG'
        else: spec = 'NORMAL'
        specialties.append(spec)
        
        # --- LOGIQUE CACHÉE (Ce que le ML doit apprendre) ---
        # Base Dwell Time
        dt = 5.0 
        
        if types[i] == 'TRANSSHIPMENT': dt -= 2.0  # Repart vite
        if types[i] == 'IMPORT': dt += 1.5         # Dédouanement prend du temps
        
        if spec == 'FRIGO': dt -= 1.5              # Urgence froid
        if spec == 'DANGER': dt -= 1.0             # Ne reste pas longtemps
        if spec == 'OOG': dt += 2.0                # Logistique complexe
        
        if sizes[i] == 40: dt += 0.5
        if weights[i] > 20: dt += 1.0              # Plus lourd = plus long à traiter
        
        if arrival_days_of_week[i] >= 5: dt += 1.5 # Arrive le weekend = attend lundi
        
        # Saisonnalité (ex: Pic en été)
        if 6 <= arrival_months[i] <= 8: dt += 1.0
        
        # Ajout de bruit aléatoire (la réalité n'est pas parfaite)
        noise = np.random.normal(0, 1.5)
        dt = max(0.5, dt + noise) # Minimum 12 heures (0.5 jour)
        
        dwell_times.append(round(dt, 2))

    df = pd.DataFrame({
        'container_id': [f"HIST-{i:06d}" for i in range(num_samples)],
        'size': sizes,
        'weight': weights,
        'type': types,
        'specialty': specialties,
        'arrival_day_of_week': arrival_days_of_week,
        'arrival_month': arrival_months,
        'dwell_time_days': dwell_times
    })
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Dataset généré avec succès : {output_file}")
    print(df.head())
    
if __name__ == "__main__":
    generate_training_data()
