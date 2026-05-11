import pandas as pd
import os
from pathlib import Path

def create_marsa_referentiel(input_path, output_path):
    print(f"Generation du Referentiel des Zones : {input_path}")
    
    # 1. Chargement des donnees
    if not os.path.exists(input_path):
        print(f"Erreur : Le fichier {input_path} est introuvable.")
        return
    
    df = pd.read_csv(input_path)
    
    # 2. Agregation par Cellule
    referentiel = df.groupby(['TERMINAL', 'BLOC', 'TRAVEE', 'CELLULE']).agg({
        'NIVEAU': 'max',
        'OCCURRENCES': 'sum'
    }).reset_index()
    
    referentiel = referentiel.rename(columns={
        'NIVEAU': 'NIVEAU_MAX_REEL',
        'OCCURRENCES': 'CAPACITE_ESTIMEE'
    })
    
    # 3. Attribution des TYPES_ADMIS
    def assign_types(row):
        bloc = str(row['BLOC'])
        if bloc in ['AE', 'Z', '02D']: return "FRIGO"
        if bloc in ['CE', 'CP', '02F']: return "DANGEREUX"
        if bloc in ['F', 'G', '02E']: return "CITERNE"
        if bloc in ['L', 'MP', '01A']: return "HORS_GABARIT"
        return "NORMAL"
    
    referentiel['TYPES_ADMIS'] = referentiel.apply(assign_types, axis=1)
    
    # 4. Classification CATEGORIE_STORAGE (Rétablissement des règles Marsa + Limites 4/6)
    def classify_storage(row):
        bloc = str(row['BLOC'])
        
        # TC3 : Blocs spécifiques pour Pleins
        if row['TERMINAL'] == 'TC3':
            if bloc in ['01A', '01B', '01C', '02D', '02E', '02F']:
                return 'ZONE_PLEIN', 4
        
        # TCE : Séries X, Y, Z pour Pleins
        else:
            if len(bloc) >= 2 and bloc.endswith(('X', 'Y', 'Z')):
                return 'ZONE_PLEIN', 4
            if bloc in ['AE', 'AX', 'AY', 'AZ', 'BE', 'BP', 'BT', 'BX', 'BY', 'BZ', 'K', 'KP', 'M', 'TP']:
                return 'ZONE_PLEIN', 4
                
        return 'ZONE_VIDE', 6
            
    res = referentiel.apply(classify_storage, axis=1)
    referentiel['CATEGORIE_STORAGE'] = [x[0] for x in res]
    referentiel['MAX_Z_LIMITE'] = [x[1] for x in res]
    
    # Export
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    referentiel.to_csv(output_path, index=False)
    
    print(f"Referentiel RESTAURÉ avec limites strictes (4 Pleins / 6 Vides) : {output_path}")
