"""
sync_iso_types_fast.py - Version rapide avec BULK UPDATE via table temporaire
"""
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

ISO_TO_SPECIALITE = {
    'DRY STANDARD':             'NORMAL',
    'REEFER':                   'FRIGO',
    'DANGEREUX (IMDG)':         'DANGEREUX',
    'TANK':                     'CITERNE',
    'OPEN TOP':                 'HORS_GABARIT',
    'FLAT RACK (HORS GABARIT)': 'HORS_GABARIT',
    'PALLET WIDE (EUROPE)':     'HORS_GABARIT',
}

p = quote_plus("Kawtar@123")
engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")

print("Chargement CSV...")
df = pd.read_csv('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/data/processed/positions_normalisees_marsa.csv')
df.columns = [c.strip().lower() for c in df.columns]
df = df.rename(columns={'bloc': 'zone', 'travee': 'allee', 'cellule': 'pile', 'niveau': 'niveau_z'})

df['allee']          = df['allee'].astype(str).str.strip()
df['pile']           = df['pile'].astype(str).str.strip()
df['niveau_z']       = df['niveau_z'].astype(str).str.strip()
df['terminal']       = df['terminal'].astype(str).str.strip().str.upper()
df['type_iso_detail']= df['type_iso_detail'].astype(str).str.strip()
df['specialite']     = df['type_iso_detail'].map(ISO_TO_SPECIALITE).fillna('NORMAL')

print(f"  -> {len(df)} lignes chargees")

# Ecrire le CSV dans une table temporaire puis faire un JOIN UPDATE
df_insert = df[['terminal','zone','allee','pile','niveau_z','type_iso_detail','specialite']].copy()

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS _iso_sync_tmp"))

df_insert.to_sql('_iso_sync_tmp', engine, if_exists='replace', index=False, chunksize=1000)
print("  -> Table de sync chargee.")

with engine.begin() as conn:
    result = conn.execute(text("""
        UPDATE conteneurs c
        JOIN _iso_sync_tmp t 
          ON c.terminal  = t.terminal
         AND c.zone      = t.zone
         AND c.allee     = t.allee
         AND c.pile      = t.pile
         AND c.niveau_z  = t.niveau_z
        SET c.type_iso_detail = t.type_iso_detail,
            c.specialite      = t.specialite
    """))
    print(f"  -> {result.rowcount} conteneurs mis a jour en DB.")
    conn.execute(text("DROP TABLE IF EXISTS _iso_sync_tmp"))

print("\nSynchronisation ISO terminee avec succes !")
