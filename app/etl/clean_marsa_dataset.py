import pandas as pd
import numpy as np
import os
import random
from datetime import datetime

def clean_marsa_dataset_v7():
    raw_path = r"c:\Users\hp\Desktop\STAGE_PFE_MARSA_MAROC\data\raw\positions_parc_marsa.csv"
    output_path = r"c:\Users\hp\Desktop\STAGE_PFE_MARSA_MAROC\data\processed\positions_normalisees_marsa.csv"
    
    print(f"[{datetime.now()}] Génération finale (Inclusion PALLET WIDE)...")
    try:
        df = pd.read_excel(raw_path)
    except:
        df = pd.read_csv(raw_path)

    # --- 1. Nettoyage & Remplissage ---
    if 'TERMINAL' in df.columns:
        cells = ['A', 'B', 'C', 'D']
        mask_tc3_empty = (df['TERMINAL'] == 'TC3') & (df['CELLULE'].isna())
        if mask_tc3_empty.any():
            df.loc[mask_tc3_empty, 'CELLULE'] = [cells[i % 4] for i in range(mask_tc3_empty.sum())]

    df['BLOC'] = df['BLOC'].fillna('Z_UNKNOWN')
    df['TRAVEE'] = df['TRAVEE'].fillna(1).astype(int)
    df['CELLULE'] = df['CELLULE'].fillna('A')

    # --- 2. Simulation des Types (Répartition Réaliste Incluant PW) ---
    types_pool = ['DV'] * 73 + ['RE'] * 10 + ['IMDG'] * 5 + ['CT'] * 4 + ['OT'] * 3 + ['FL'] * 3 + ['PW'] * 2
    df['RAW_TYPE'] = [random.choice(types_pool) for _ in range(len(df))]

    iso_map = {
        'DV': 'DRY STANDARD', 'RE': 'REEFER', 'OT': 'OPEN TOP', 'CT': 'TANK',
        'FL': 'FLAT RACK (HORS GABARIT)', 'IMDG': 'DANGEREUX (IMDG)',
        'PW': 'PALLET WIDE (EUROPE)'
    }
    df['TYPE_ISO_DETAIL'] = df['RAW_TYPE'].map(iso_map)

    # --- 3. Zones & Flux ---
    blocs = df['BLOC'].unique()
    vessels = ['MSC LEVANTE', 'CMA CGM MARCO POLO', 'MAERSK ALGEciras', 'EVER GIVEN', 'HAPAG LLOYD HAMBURG']
    pods = ['VALENCIA', 'BARCELONA', 'GENOVA', 'FOS-SUR-MER', 'ALGEciras']
    bloc_config = {b: {'ZONE': 'VIDE' if random.random() < 0.65 else 'PLEIN',
                       'FLUX': 'IMPORT' if random.random() < 0.5 else 'EXPORT'} for b in blocs}

    # --- 4. Ré-empilage Physique avec Sécurité ---
    df['IS_OOG'] = df['RAW_TYPE'].isin(['OT', 'FL']).astype(int)
    df = df.sort_values(by=['TERMINAL', 'BLOC', 'TRAVEE', 'CELLULE', 'IS_OOG'], ascending=[True, True, True, True, False])
    
    final_rows = []
    douane_options = ['Main levée', 'Facturé', 'En cours']
    pile_counters = {}

    for _, row in df.iterrows():
        term = row['TERMINAL']
        b_name = row['BLOC']
        tr = int(row['TRAVEE'])
        cl = row['CELLULE']
        t_iso = row['TYPE_ISO_DETAIL']
        config = bloc_config.get(b_name, {'ZONE': 'PLEIN', 'FLUX': 'IMPORT'})
        
        stack_id = (term, b_name, tr, cl)
        pile_counters[stack_id] = pile_counters.get(stack_id, 0) + 1
        current_lvl = pile_counters[stack_id]
        
        limit = 6 if config['ZONE'] == 'VIDE' else (3 if term == 'TCE' else 5)
        
        if current_lvl > limit:
            cl = chr(ord(cl[0]) + 1) if len(cl)==1 and cl.isalpha() else cl + "2"
            stack_id = (term, b_name, tr, cl)
            pile_counters[stack_id] = pile_counters.get(stack_id, 0) + 1
            current_lvl = pile_counters[stack_id]

        if config['FLUX'] == 'IMPORT':
            status_d, vessel, pod = random.choice(douane_options), '', ''
        else:
            status_d, vessel, pod = '', random.choice(vessels), random.choice(pods)

        final_rows.append({
            'TERMINAL': term, 'BLOC': b_name, 'TRAVEE': tr, 'CELLULE': cl, 'NIVEAU': current_lvl,
            'TYPE_ISO_DETAIL': t_iso, 'TYPE_ZONE': config['ZONE'], 'FLUX': config['FLUX'],
            'STATUS_DOUANE': status_d, 'NOM_NAVIRE': vessel, 'POD': pod
        })

    df_final = pd.DataFrame(final_rows)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[{datetime.now()}] Export V7 terminé avec PALLET WIDE.")

if __name__ == "__main__":
    clean_marsa_dataset_v7()
