"""
📦 Script d'Import des Positions dans MySQL
============================================
Charge positions_restructurees.csv dans la table conteneurs

Usage:
  python app/database/import_positions_final.py
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration DB
db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
db_port = os.getenv("MYSQL_PORT", "3306")
db_user = os.getenv("MYSQL_USER", "root")
db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")

engine = create_engine(
    f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
    pool_pre_ping=True
)

# Chemins
DATA_DIR = Path(__file__).parent.parent.parent / "data"
INPUT_FILE = DATA_DIR / "processed" / "positions_restructurees.csv"

print("=" * 70)
print("📦 IMPORT DES POSITIONS STRUCTURÉES DANS MYSQL")
print("=" * 70)

# 1. VÉRIFIER LE FICHIER
if not INPUT_FILE.exists():
    print(f"❌ Fichier non trouvé: {INPUT_FILE}")
    exit(1)

print(f"\n✓ Chargement du CSV: {INPUT_FILE}")
df = pd.read_csv(INPUT_FILE)
print(f"  → {df.shape[0]} conteneurs à importer")

# 2. PRÉPARER LES DONNÉES POUR MYSQL
print("\n✓ Conversion des types de données...")
df['HORODATAGE'] = pd.to_datetime(df['HORODATAGE'])
df['DEPARTURE_TIME'] = pd.to_datetime(df['DEPARTURE_TIME'])

# Mapper les colonnes pour la table conteneurs
df_import = df.rename(columns={
    'CONTAINER_ID': 'container_id',
    'HORODATAGE': 'date_arrivee',
    'DEPARTURE_TIME': 'departure_time',
    'TERMINAL': 'terminal',
    'BLOC': 'zone',
    'TRAVEE': 'allee',
    'CELLULE': 'pile',
    'NIVEAU': 'niveau_z',
    'SLOT': 'slot',
    'TYPE_ISO_DETAIL': 'type_conteneur',
    'IS_IMDG': 'is_imdg',
    'IS_REEFER': 'is_reefer',
    'SIZE': 'size',
    'FLUX': 'flux',
    'WEIGHT': 'weight',
    'STATUS_DOUANE': 'status_douane',
    'NOM_NAVIRE': 'nom_navire',
    'POD': 'pod',
    'TYPE_ZONE': 'type_zone'
}).copy()

# Ajouter les colonnes manquantes
df_import['reference'] = df_import['container_id']
df_import['status'] = 'STOCKED'
df_import['created_at'] = pd.Timestamp.now()

print("  → Colonnes mappées")

# 3. VÉRIFIER LA CONNEXION DB
print("\n✓ Vérification de la connexion MySQL...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DATABASE()"))
        print(f"  ✅ Connecté à: {result.scalar()}")
except Exception as e:
    print(f"  ❌ Erreur de connexion: {e}")
    exit(1)

# 4. VIDER LA TABLE (optionnel - décommentez si nécessaire)
# print("\n⚠️  Vidage de la table conteneurs...")
# with engine.begin() as conn:
#     conn.execute(text("DELETE FROM conteneurs"))
#     conn.commit()
# print("  ✓ Table vidée")

# 5. IMPORTER LES DONNÉES
print("\n✓ Import des données dans MySQL...")
try:
    # Garder seulement les colonnes compatibles avec la table
    colonnes_db = [
        'container_id', 'reference', 'date_arrivee', 'departure_time',
        'terminal', 'zone', 'allee', 'pile', 'niveau_z', 'slot',
        'type_conteneur', 'type_zone', 'size', 'flux', 'weight',
        'status_douane', 'is_imdg', 'is_reefer', 'status',
        'nom_navire', 'pod'
    ]
    
    df_import_clean = df_import[colonnes_db].copy()
    
    # Importer en chunks
    chunksize = 500
    total = len(df_import_clean)
    
    for i in range(0, total, chunksize):
        chunk = df_import_clean[i:i+chunksize]
        chunk.to_sql('conteneurs', engine, if_exists='append', index=False)
        percent = min((i + chunksize) / total * 100, 100)
        print(f"  → Progression: {percent:.1f}% ({i+len(chunk)}/{total})")
    
    print(f"\n  ✅ {total} conteneurs importés avec succès!")
    
except Exception as e:
    print(f"  ❌ Erreur lors de l'import: {e}")
    exit(1)

# 6. VÉRIFIER L'IMPORT
print("\n✓ Vérification des données importées...")
try:
    with engine.connect() as conn:
        # Compter les enregistrements
        count = conn.execute(text("SELECT COUNT(*) FROM conteneurs")).scalar()
        print(f"  → Total conteneurs en DB: {count}")
        
        # Compter par TERMINAL
        terminals = conn.execute(text("""
            SELECT terminal, COUNT(*) as count 
            FROM conteneurs 
            GROUP BY terminal 
            ORDER BY count DESC
        """)).fetchall()
        print(f"  → Distribution par terminal:")
        for term, cnt in terminals:
            print(f"    - {term}: {cnt}")
        
        # Compter par FLUX
        flux_count = conn.execute(text("""
            SELECT flux, COUNT(*) as count 
            FROM conteneurs 
            GROUP BY flux
        """)).fetchall()
        print(f"  → Distribution par flux:")
        for flx, cnt in flux_count:
            print(f"    - {flx}: {cnt}")

except Exception as e:
    print(f"  ⚠️  Erreur lors de la vérification: {e}")

print("\n" + "=" * 70)
print("✅ IMPORT COMPLÉTÉ!")
print("=" * 70)
