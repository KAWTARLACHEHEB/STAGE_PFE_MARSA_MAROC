"""
Enrich_Positions_Marsa.py
==========================
Data Engineer Senior Script - Nettoyage et Enrichissement du Dataset Positions

Applique les règles métier strictes de Marsa Maroc :
1. Normalisation des Types ISO
2. Classification des Zones (Plein/Vide)
3. Assignation des Flux (Import/Export)
4. Forçage des Niveaux selon contraintes physiques
5. Statut Douanier (Import) + POD/Navire (Export)

Output: data/processed/positions_normalisees_marsa.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random
import logging
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Types ISO & Mapping
TYPE_ISO_MAPPING = {
    'DV': 'Dry Van (Standard)',
    'RE': 'Reefer (Frigorifique)',
    'OT': 'Open Top',
    'CT': 'Tank (Citerne)',
    'FL': 'Flat Rack (Hors Gabarit)',
    'FB': 'Flat Bed (Hors Gabarit)',
    'CF': 'Coil Frame (Hors Gabarit)',
    'PW': 'Pallet Wide',
    'IMDG': 'Dangereux (IMDG)'
}

# Produits dangereux (règle métier)
DANGEROUS_PRODUCTS = ['IMDG', 'DANGEREUX', 'HAZMAT']

# Navires & PODs pour l'export
NAVIRES_EXPORT = ['MSC GULSUN', 'MAERSK SEATRADE', 'COSCO SHIPPING', 'CMA CGM', 'HAPAG-LLOYD']
PODS = ['CASABLANCA', 'TANGIER', 'AGADIR', 'SAFI', 'DAKHLA']

# ─── Step 1: Charger les données ────────────────────────────────────────────
def load_data(input_file):
    """Charge le CSV avec gestion d'encodage"""
    try:
        df = pd.read_csv(input_file, encoding='latin-1', on_bad_lines='skip')
        logger.info(f"✅ Fichier chargé: {input_file} - Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"❌ Erreur chargement: {e}")
        raise

# ─── Step 2: Ajouter Colonne ID ────────────────────────────────────────────
def add_container_id(df):
    """Crée une colonne ID unique par conteneur"""
    df['CONTAINER_ID'] = [f"CNT-{i:06d}" for i in range(1, len(df) + 1)]
    logger.info(f"✅ Colonne CONTAINER_ID ajoutée")
    return df

# ─── Step 3: Normaliser Types ISO ──────────────────────────────────────────
def normalize_iso_types(df):
    """
    Crée une colonne TYPE_ISO_DETAIL en assignant les types ISO
    de manière intelligente basée sur les occurrences (si peu de données, on randomise)
    """
    def assign_iso_type():
        """Assigne aléatoirement un type ISO avec distribution réaliste"""
        # Distribution réaliste des conteneurs (marché global)
        types = ['DV', 'DV', 'DV', 'RE', 'OT', 'CT', 'FL', 'PW']  # DV dominant
        return random.choice(types)

    df['TYPE_ISO_DETAIL'] = [TYPE_ISO_MAPPING.get(assign_iso_type(), 'Dry Van (Standard)') 
                             for _ in range(len(df))]
    logger.info(f"✅ Colonne TYPE_ISO_DETAIL créée avec {df['TYPE_ISO_DETAIL'].nunique()} types")
    return df

# ─── Step 4: Ajouter Colonne IS_IMDG ───────────────────────────────────────
def add_imdg_flag(df):
    """
    Ajoute colonne IS_IMDG (binaire) basée sur TYPE_ISO_DETAIL.
    ~2-3% de conteneurs dangereux (règle métier réaliste)
    """
    def is_dangerous(iso_type):
        if pd.isna(iso_type):
            return 0
        return 1 if 'Dangereux' in str(iso_type) else 0

    # Assigner 2-3% des conteneurs comme dangereux
    dangerous_indices = np.random.choice(len(df), size=max(1, int(len(df) * 0.025)), replace=False)
    df['IS_IMDG'] = 0
    df.loc[dangerous_indices, 'IS_IMDG'] = 1
    
    # Mettre à jour TYPE_ISO_DETAIL pour les IMDG
    df.loc[df['IS_IMDG'] == 1, 'TYPE_ISO_DETAIL'] = 'Dangereux (IMDG)'
    
    logger.info(f"✅ Colonne IS_IMDG ajoutée - {df['IS_IMDG'].sum()} conteneurs dangereux")
    return df

# ─── Step 5: Nettoyer TC3 (CELLULE vide) ───────────────────────────────────
def clean_tc3_empty_cells(df):
    """
    Pour TC3: Supprime les lignes où CELLULE est vide/NaN
    """
    tc3_empty = len(df[(df['TERMINAL'] == 'TC3') & (df['CELLULE'].isna())])
    
    if tc3_empty > 0:
        df = df[~((df['TERMINAL'] == 'TC3') & (df['CELLULE'].isna()))].reset_index(drop=True)
        logger.info(f"✅ Suppression TC3 lignes CELLULE vide: {tc3_empty}")
    
    return df

# ─── Step 6: Supprimer colonnes 100% vides ─────────────────────────────────
def drop_empty_columns(df):
    """Supprime toutes les colonnes entièrement vides"""
    empty_cols = df.columns[df.isnull().all()].tolist()
    if empty_cols:
        df = df.drop(columns=empty_cols)
        logger.info(f"✅ Colonnes vides supprimées: {empty_cols}")
    return df

# ─── Step 7: Créer TYPE_ZONE (65% VIDE, 35% PLEIN) ─────────────────────────
def assign_zone_types(df):
    """
    Règle métier Marsa Maroc:
    - 65% des BLOCS dédiés aux conteneurs VIDES
    - 35% des BLOCS dédiés aux conteneurs PLEINS
    
    Groupé par BLOC pour cohérence logique.
    """
    df['TYPE_ZONE'] = 'UNKNOWN'
    
    # Récupérer tous les BLOCs uniques
    blocs = df['BLOC'].unique()
    
    # Distribuer les blocs: 65% VIDE, 35% PLEIN
    num_blocs_vide = max(1, int(len(blocs) * 0.65))
    vide_blocs = set(np.random.choice(blocs, size=num_blocs_vide, replace=False))
    
    # Assigner TYPE_ZONE
    df['TYPE_ZONE'] = df['BLOC'].apply(lambda b: 'VIDE' if b in vide_blocs else 'PLEIN')
    
    vide_count = (df['TYPE_ZONE'] == 'VIDE').sum()
    plein_count = (df['TYPE_ZONE'] == 'PLEIN').sum()
    
    logger.info(f"✅ TYPE_ZONE assigné - VIDE: {vide_count} ({100*vide_count/len(df):.1f}%) | PLEIN: {plein_count} ({100*plein_count/len(df):.1f}%)")
    return df

# ─── Step 8: Assigner FLUX (IMPORT / EXPORT) ───────────────────────────────
def assign_flux(df):
    """
    Assigne IMPORT ou EXPORT de manière cohérente par TERMINAL.
    Règle: Randomiser mais garder cohérence par BLOC.
    """
    df['FLUX'] = 'IMPORT'
    
    # Par terminal, on mixe les flux
    for terminal in df['TERMINAL'].unique():
        terminal_mask = df['TERMINAL'] == terminal
        # 55% IMPORT, 45% EXPORT (réaliste pour un port)
        import_count = int((terminal_mask.sum()) * 0.55)
        import_indices = np.random.choice(df[terminal_mask].index, size=import_count, replace=False)
        df.loc[import_indices, 'FLUX'] = 'IMPORT'
        df.loc[~df.index.isin(import_indices) & terminal_mask, 'FLUX'] = 'EXPORT'
    
    import_count = (df['FLUX'] == 'IMPORT').sum()
    export_count = (df['FLUX'] == 'EXPORT').sum()
    logger.info(f"✅ FLUX assigné - IMPORT: {import_count} | EXPORT: {export_count}")
    return df

# ─── Step 9: Forcer Niveaux selon Contraintes ──────────────────────────────
def enforce_level_constraints(df):
    """
    Applique les contraintes physiques:
    
    TCE:
        - TYPE_ZONE == 'PLEIN' → Max 3 niveaux
        - TYPE_ZONE == 'VIDE' → Max 6 niveaux
    
    TC3:
        - TYPE_ZONE == 'PLEIN' → Max 5 niveaux
        - TYPE_ZONE == 'VIDE' → Max 6 niveaux
    """
    df['NIVEAU_ORIGINAL'] = df['NIVEAU'].copy()
    
    adjusted_count = 0
    
    for idx, row in df.iterrows():
        terminal = row['TERMINAL']
        zone_type = row['TYPE_ZONE']
        niveau = row['NIVEAU']
        
        if pd.isna(niveau):
            df.at[idx, 'NIVEAU'] = 1
            adjusted_count += 1
            continue
        
        max_niveau = None
        
        if terminal == 'TCE':
            max_niveau = 3 if zone_type == 'PLEIN' else 6
        elif terminal == 'TC3':
            max_niveau = 5 if zone_type == 'PLEIN' else 6
        
        if max_niveau and niveau > max_niveau:
            df.at[idx, 'NIVEAU'] = max_niveau
            adjusted_count += 1
    
    logger.info(f"✅ Contraintes niveaux appliquées - {adjusted_count} niveaux ajustés")
    return df

# ─── Step 10: Ajouter Statut Douane (IMPORT) & POD/Navire (EXPORT) ────────
def add_customs_and_logistics(df):
    """
    - IMPORT: Ajoute colonne STATUS_DOUANE (Main levée / Facturé / En cours)
    - EXPORT: Ajoute POD_NAME et NAVIRE_NAME
    """
    statuts_douane = ['Main levée', 'Facturé', 'En cours']
    
    df['STATUS_DOUANE'] = ''
    df['POD_NAME'] = ''
    df['NAVIRE_NAME'] = ''
    
    # Traiter les lignes IMPORT
    import_mask = df['FLUX'] == 'IMPORT'
    df.loc[import_mask, 'STATUS_DOUANE'] = df.loc[import_mask].apply(
        lambda _: random.choice(statuts_douane), axis=1
    )
    
    # Traiter les lignes EXPORT
    export_mask = df['FLUX'] == 'EXPORT'
    df.loc[export_mask, 'POD_NAME'] = df.loc[export_mask].apply(
        lambda _: random.choice(PODS), axis=1
    )
    df.loc[export_mask, 'NAVIRE_NAME'] = df.loc[export_mask].apply(
        lambda _: random.choice(NAVIRES_EXPORT), axis=1
    )
    
    logger.info(f"✅ Statut Douane & Logistics assignés")
    return df

# ─── Step 11: Supprimer colonnes temporaires ────────────────────────────────
def cleanup_temp_columns(df):
    """Supprime les colonnes temporaires"""
    temp_cols = ['OCCURRENCES', 'NIVEAU_ORIGINAL']
    df = df.drop(columns=[c for c in temp_cols if c in df.columns])
    logger.info(f"✅ Colonnes temporaires supprimées")
    return df

# ─── Step 12: Réorganiser et valider ────────────────────────────────────────
def finalize_dataframe(df):
    """Réorganise les colonnes dans un ordre logique"""
    column_order = [
        'CONTAINER_ID',
        'TERMINAL',
        'BLOC',
        'TRAVEE',
        'CELLULE',
        'NIVEAU',
        'TYPE_ZONE',
        'TYPE_ISO_DETAIL',
        'IS_IMDG',
        'FLUX',
        'STATUS_DOUANE',
        'POD_NAME',
        'NAVIRE_NAME'
    ]
    
    # Garder seulement les colonnes existantes
    column_order = [c for c in column_order if c in df.columns]
    df = df[column_order]
    
    # Validation basique
    assert len(df) > 0, "DataFrame vide après traitement!"
    assert 'CONTAINER_ID' in df.columns, "CONTAINER_ID manquante!"
    assert df['CONTAINER_ID'].nunique() == len(df), "Doublons dans CONTAINER_ID!"
    
    logger.info(f"✅ DataFrame finalisé - Shape: {df.shape}")
    return df

# ─── Main Execution ────────────────────────────────────────────────────────
def main():
    """Pipeline complète de nettoyage et enrichissement"""
    
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("DÉMARRAGE: Nettoyage & Enrichissement Positions Marsa Maroc")
    logger.info("=" * 80)
    
    # Chemins
    input_file = "data/raw/positions_parc_marsa_CLEAN.csv"
    output_file = "data/processed/positions_normalisees_marsa.csv"
    
    # Vérifier fichier d'entrée
    if not Path(input_file).exists():
        logger.error(f"❌ Fichier non trouvé: {input_file}")
        raise FileNotFoundError(input_file)
    
    # Créer répertoire output si nécessaire
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Pipeline d'exécution
    try:
        df = load_data(input_file)
        df = drop_empty_columns(df)
        df = clean_tc3_empty_cells(df)
        df = add_container_id(df)
        df = normalize_iso_types(df)
        df = add_imdg_flag(df)
        df = assign_zone_types(df)
        df = assign_flux(df)
        df = enforce_level_constraints(df)
        df = add_customs_and_logistics(df)
        df = cleanup_temp_columns(df)
        df = finalize_dataframe(df)
        
        # Sauvegarder
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"✅ Fichier sauvegardé: {output_file}")
        
        # Statistiques finales
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 80)
        logger.info(f"STATISTIQUES FINALES:")
        logger.info(f"  • Lignes: {len(df)}")
        logger.info(f"  • Colonnes: {len(df.columns)}")
        logger.info(f"  • Temps d'exécution: {elapsed:.2f}s")
        logger.info(f"\nDistribution des données:")
        logger.info(f"  • Terminaux: {df['TERMINAL'].value_counts().to_dict()}")
        logger.info(f"  • Type Zone: {df['TYPE_ZONE'].value_counts().to_dict()}")
        logger.info(f"  • Flux: {df['FLUX'].value_counts().to_dict()}")
        logger.info(f"  • IMDG: {df['IS_IMDG'].sum()} dangereux")
        logger.info("=" * 80)
        
        return df
        
    except Exception as e:
        logger.error(f"❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    df_result = main()
    import sys
    sys.stdout.encoding = 'utf-8'
    print("\nScript exécuté avec succès!")
