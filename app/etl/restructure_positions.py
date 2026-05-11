"""
🔧 Script de Restructuration Complète du Dataset
================================================
Enrichit et structure positions_normalisees_marsa.csv pour l'API et MySQL

Ajouts :
- CONTAINER_ID (identifiant unique)
- DEPARTURE_TIME (dates de départ)
- WEIGHT (poids des conteneurs)
- HORODATAGE (timestamp)
- Remplissage des valeurs NULL
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Chemins
DATA_DIR = Path(__file__).parent.parent.parent / "data"
INPUT_FILE = DATA_DIR / "processed" / "positions_normalisees_marsa.csv"
OUTPUT_FILE = DATA_DIR / "processed" / "positions_restructurees.csv"

print("=" * 70)
print("🔄 RESTRUCTURATION DU DATASET MARSA MAROC")
print("=" * 70)

# 1. CHARGER LE CSV
print("\n✓ Chargement du CSV...")
df = pd.read_csv(INPUT_FILE)
print(f"  → Dimensions initiales: {df.shape}")

# 2. CRÉER CONTAINER_ID UNIQUE
print("\n✓ Génération des CONTAINER_ID...")
# Format: MARSA-TERMINAL-BLOC-TRAVEE-CELLULE-NIVEAU-TIMESTAMP
df['CONTAINER_ID'] = (
    'MARSA-' +
    df['TERMINAL'].astype(str) + '-' +
    df['BLOC'].astype(str) + '-' +
    df['TRAVEE'].astype(str).str.zfill(3) + '-' +
    df['CELLULE'].astype(str) + '-' +
    df['NIVEAU'].astype(str) +
    '-' + pd.Series(np.random.randint(1000, 9999, len(df))).astype(str)
)

# 3. AJOUTER HORODATAGE (timestamp aléatoire sur 6 mois)
print("✓ Génération des horodatages...")
base_date = datetime(2025, 11, 1)
df['HORODATAGE'] = [
    base_date + timedelta(days=random.randint(0, 180), 
                          hours=random.randint(0, 23),
                          minutes=random.randint(0, 59))
    for _ in range(len(df))
]

# 4. AJOUTER DEPARTURE_TIME (basé sur le statut)
print("✓ Calcul des DEPARTURE_TIME...")
def calculate_departure(row):
    base = row['HORODATAGE']
    
    if row['FLUX'] == 'EXPORT':
        # EXPORT : départ dans 2-5 jours
        return base + timedelta(days=random.randint(2, 5))
    else:  # IMPORT
        # IMPORT : départ dans 5-15 jours
        return base + timedelta(days=random.randint(5, 15))

df['DEPARTURE_TIME'] = df.apply(calculate_departure, axis=1)

# 5. AJOUTER WEIGHT (poids)
print("✓ Génération des poids...")
def assign_weight(row):
    if row['TYPE_ZONE'] == 'PLEIN':
        return round(random.uniform(15000, 28000), 2)  # Conteneur plein 15-28 tonnes
    else:
        return round(random.uniform(2000, 5000), 2)    # Conteneur vide 2-5 tonnes

df['WEIGHT'] = df.apply(assign_weight, axis=1)

# 6. ENRICHIR STATUS_DOUANE (IMPORT seulement)
print("✓ Remplissage STATUS_DOUANE...")
statuts = ['Main levée', 'Facturé', 'En cours', 'En attente', 'Dédouané']
mask_import_null = (df['FLUX'] == 'IMPORT') & (df['STATUS_DOUANE'].isna())
df.loc[mask_import_null, 'STATUS_DOUANE'] = np.random.choice(statuts, size=mask_import_null.sum())
df['STATUS_DOUANE'] = df['STATUS_DOUANE'].fillna('')

# 7. ENRICHIR NOM_NAVIRE et POD (EXPORT seulement)
print("✓ Remplissage NOM_NAVIRE et POD...")
navires = ['HAPAG LLOYD HAMBURG', 'MAERSK COPENHAGEN', 'MSC GULSUN', 'EVER GIVEN',
           'CMA CGM ANTOINE', 'ONE INNOVATION', 'TRANSATLANTIC BRIDGE']
ports = ['VALENCIA', 'BARCELONA', 'GENOVA', 'FOS-SUR-MER', 'ROTTERDAM', 'HAMBOURG', 'ANVERS']

mask_export_null = (df['FLUX'] == 'EXPORT') & (df['NOM_NAVIRE'].isna())
df.loc[mask_export_null, 'NOM_NAVIRE'] = np.random.choice(navires, size=mask_export_null.sum())
df.loc[mask_export_null, 'POD'] = np.random.choice(ports, size=mask_export_null.sum())

df['NOM_NAVIRE'] = df['NOM_NAVIRE'].fillna('')
df['POD'] = df['POD'].fillna('')

# 8. AJOUTER COLONNES MANQUANTES
print("✓ Ajout de colonnes supplémentaires...")
df['SLOT'] = df['BLOC'] + '-' + df['TRAVEE'].astype(str) + df['CELLULE'] + '-N' + df['NIVEAU'].astype(str)
df['IS_IMDG'] = df['TYPE_ISO_DETAIL'].str.contains('DANGER|IMDG', case=False, na=False).astype(int)
df['IS_REEFER'] = (df['TYPE_ISO_DETAIL'] == 'REEFER').astype(int)
df['SIZE'] = df['TYPE_ISO_DETAIL'].apply(lambda x: '40' if 'FLAT' in x or 'OPEN' in x else '20')

# 9. RÉORGANISER LES COLONNES
print("✓ Réorganisation des colonnes...")
colonnes_finales = [
    'CONTAINER_ID', 'HORODATAGE', 'TERMINAL', 'BLOC', 'TRAVEE', 'CELLULE', 'NIVEAU',
    'SLOT', 'TYPE_ZONE', 'TYPE_ISO_DETAIL', 'IS_IMDG', 'IS_REEFER', 'SIZE',
    'FLUX', 'WEIGHT', 'STATUS_DOUANE', 'DEPARTURE_TIME',
    'NOM_NAVIRE', 'POD'
]
df = df[colonnes_finales]

# 10. VALIDER ET SAUVEGARDER
print("✓ Validation...")
print(f"  → Doublons: {df.duplicated().sum()}")
print(f"  → Valeurs NULL: {df.isnull().sum().sum()}")
print(f"  → Dimensions finales: {df.shape}")

print("\n✓ Sauvegarde du CSV restructuré...")
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"  ✅ Fichier sauvegardé: {OUTPUT_FILE}")

# 11. AFFICHER UN APERÇU
print("\n" + "=" * 70)
print("📊 APERÇU DU DATASET RESTRUCTURÉ")
print("=" * 70)
print(f"\nShape: {df.shape}")
print(f"\nColonnes: {', '.join(df.columns.tolist())}")
print(f"\nTypes de données:\n{df.dtypes}")
print(f"\nPremières lignes:\n{df.head(10).to_string()}")
print(f"\nStatistiques:\n{df.describe()}")

print("\n" + "=" * 70)
print("✅ RESTRUCTURATION COMPLÈTE!")
print("=" * 70)
