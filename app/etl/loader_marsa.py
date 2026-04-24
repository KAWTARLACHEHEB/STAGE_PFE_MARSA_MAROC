import pandas as pd
import numpy as np
import io
import sys

def load_marsa_csv_robust(file_path):
    """
    Lit le fichier Marsa (TC3) en gérant les colonnes en trop 
    et en capturant les données 'EXTRA' comme le 305.
    """
    print(f"Tentative de lecture robuste de : {file_path}")
    
    try:
        # 1. On lit d'abord le fichier ligne par ligne pour détecter le nombre max de colonnes
        # C'est la seule façon de ne pas perdre de données si certaines lignes ont 10 colonnes et d'autres 12
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # On calcule le nombre max de colonnes réelles dans le fichier
        max_cols = 0
        for line in lines:
            cols = len(line.split(',')) # ou ';' selon le séparateur
            if cols > max_cols:
                max_cols = cols
        
        print(f"Nombre max de colonnes detectees : {max_cols}")

        # 2. On recharge avec pandas en forçant un nombre de colonnes suffisant
        # On crée des noms de colonnes génériques au départ
        col_names = [f"COL_{i}" for i in range(max_cols)]
        
        df = pd.read_csv(
            file_path,
            names=col_names,
            sep=None,
            engine='python',
            on_bad_lines='warn',
            header=None,
            skiprows=1 # On saute l'ancien header pour le redéfinir proprement
        )

        # 3. On tente de mapper les colonnes connues
        # (A adapter selon le vrai header du fichier)
        known_headers = ['id', 'size', 'weight', 'departure_time', 'type', 'slot']
        
        # On renomme les premières colonnes
        mapping = {f"COL_{i}": header for i, header in enumerate(known_headers)}
        df = df.rename(columns=mapping)

        # 4. On crée la colonne 'EXTRA' avec tout ce qui dépasse
        extra_cols = [f"COL_{i}" for i in range(len(known_headers), max_cols)]
        if extra_cols:
            df['EXTRA'] = df[extra_cols].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
            # On supprime les colonnes COL_X intermédiaires
            df = df.drop(columns=extra_cols)

        # 5. Nettoyage final (votre logique)
        df.columns = df.columns.str.strip()
        df = df.fillna("INCONNU")
        
        print("Succes ! Le fichier est charge avec capture des donnees EXTRA.")
        print(df.head())
        return df

    except Exception as e:
        print(f"Erreur de lecture : {e}")
        return None

if __name__ == "__main__":
    # Test sur votre fichier
    df = load_marsa_csv_robust('data/raw/positions_parc_marsa_CLEAN.csv')
