import pandas as pd
import os
from pathlib import Path

def create_marsa_referentiel(input_path, output_path):
    print(f"Generation du Referentiel des Zones : {input_path}")
    
    # 1. Chargement des donnees reparees
    if not os.path.exists(input_path):
        print(f"Erreur : Le fichier {input_path} est introuvable.")
        return
    
    df = pd.read_csv(input_path)
    
    # 2. Agregation par Cellule au sol (Groupe strategique)
    # On groupe par Terminal, Bloc, Travee et Cellule
    referentiel = df.groupby(['TERMINAL', 'BLOC', 'TRAVEE', 'CELLULE']).agg({
        'NIVEAU': 'max',
        'OCCURRENCES': 'sum'
    }).reset_index()
    
    # Remplacement des noms de colonnes pour clarte
    referentiel = referentiel.rename(columns={
        'NIVEAU': 'NIVEAU_MAX',
        'OCCURRENCES': 'CAPACITE_TOTALE_EVP'
    })
    
    # 3. Classification CATEGORIE_STORAGE (Stratégie PFE Marsa Maroc)
    def classify_storage(row):
        bloc = str(row['BLOC'])
        niveau = row['NIVEAU_MAX']
        
        # PRIORITÉ 1 : Blocs Stratégiques pour les PLEINS (Bridage à Niveau 4)
        if row['TERMINAL'] == 'TC3':
            # On ne garde que les blocs Import/Export majeurs
            if bloc in ['01A', '01B', '02D']:
                return 'ZONE_PLEIN'
        else: # TCE
            # On ne garde que les "coeurs" du parc (Séries X, Y, Z)
            if len(bloc) >= 2 and bloc.endswith(('X', 'Y', 'Z')):
                return 'ZONE_PLEIN'
                
        # PRIORITÉ 2 : Spécialisation TC3 (02E/02F sont des zones de rotation VIDE)
        if row['TERMINAL'] == 'TC3' and bloc in ['02E', '02F']:
            return 'ZONE_VIDE'
            
        # PRIORITÉ 3 : Seuil de Sécurité (Le reste passe en VIDE si > 4 niveaux)
        if niveau >= 5:
            return 'ZONE_VIDE'
        
        # Par défaut, VIDE pour le reste
        return 'ZONE_VIDE'
            
    referentiel['CATEGORIE_STORAGE'] = referentiel.apply(classify_storage, axis=1)
    
    # 4. Attribution des TYPES_ADMIS (Regles Metier Marsa Maroc)
    def assign_types(row):
        types = ["NORMAL"] # Toujours admis
        
        # Regle Frigo (Blocks AE, 02D, 10F, Z, A, B)
        # On elargit pour que l'IA ait du choix
        if row['BLOC'] in ['AE', '02D', '10F', 'A', 'Z', '01A']:
            types.append("FRIGO")
            
        # Regle Matiere Dangereuse (Block 02F, 11G, C, D)
        if row['BLOC'] in ['02F', '11G', 'C', 'D', '02F']:
            types.append("DANGEREUX")
            types.append("CITERNES")
            
        # Regle Hors Gabarit (OOG) - Dans toutes les zones Plein et certains blocs specifiques
        if row['CATEGORIE_STORAGE'] == 'ZONE_PLEIN' or row['BLOC'] in ['L', 'MP']:
            types.append("HORS_GABARIT")
            
        return ", ".join(types)
    
    referentiel['TYPES_ADMIS'] = referentiel.apply(assign_types, axis=1)
    
    # 5. Finalisation et Export
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    referentiel.to_csv(output_path, index=False)
    
    print(f"Referentiel cree avec succes : {output_path}")
    print(f"Statistiques : {len(referentiel)} cellules uniques repertoriees.")
    
    # Petit aperçu
    print("\n--- Apercu du Referentiel ---")
    print(referentiel.head())

if __name__ == "__main__":
    input_file = "data/processed/positions_finales_reparees.csv"
    output_file = "data/processed/referentiel_zones_marsa.csv"
    create_marsa_referentiel(input_file, output_file)
