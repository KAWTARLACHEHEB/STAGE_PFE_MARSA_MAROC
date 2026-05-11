"""
sync_iso_types.py - Synchronise type_iso_detail du CSV vers la base de donnees
et cree la correspondance avec la specialite pour les filtres frontend.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Mapping TYPE_ISO_DETAIL (CSV) -> specialite (DB)
ISO_TO_SPECIALITE = {
    'DRY STANDARD':            'NORMAL',
    'REEFER':                  'FRIGO',
    'DANGEREUX (IMDG)':        'DANGEREUX',
    'TANK':                    'CITERNE',
    'OPEN TOP':                'HORS_GABARIT',
    'FLAT RACK (HORS GABARIT)':'HORS_GABARIT',
    'PALLET WIDE (EUROPE)':    'HORS_GABARIT',
}

p = quote_plus("Kawtar@123")
engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")

print("Chargement du dataset CSV...")
df = pd.read_csv(
    'c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/data/processed/positions_normalisees_marsa.csv'
)
df.columns = [c.strip().lower() for c in df.columns]
df = df.rename(columns={'bloc': 'zone', 'travee': 'allee', 'cellule': 'pile', 'niveau': 'niveau_z'})
df['allee'] = df['allee'].astype(str).str.strip()
df['pile'] = df['pile'].astype(str).str.strip()
df['niveau_z'] = df['niveau_z'].astype(str).str.strip()
df['terminal'] = df['terminal'].astype(str).str.strip().str.upper()
df['type_iso_detail'] = df['type_iso_detail'].astype(str).str.strip()
df['specialite_mapped'] = df['type_iso_detail'].map(ISO_TO_SPECIALITE).fillna('NORMAL')

print(f"  -> {len(df)} lignes chargees.")
print(f"  -> Types ISO uniques : {df['type_iso_detail'].unique().tolist()}")

with engine.begin() as conn:
    updated = 0
    skipped = 0

    for _, row in df.iterrows():
        result = conn.execute(text("""
            UPDATE conteneurs
            SET type_iso_detail = :iso, specialite = :spec
            WHERE terminal = :term
              AND zone      = :zone
              AND allee     = :allee
              AND pile      = :pile
              AND niveau_z  = :niv
        """), {
            "iso":   row['type_iso_detail'],
            "spec":  row['specialite_mapped'],
            "term":  row['terminal'],
            "zone":  row['zone'],
            "allee": row['allee'],
            "pile":  row['pile'],
            "niv":   row['niveau_z'],
        })
        if result.rowcount > 0:
            updated += 1
        else:
            skipped += 1

    print(f"\nResultat : {updated} conteneurs mis a jour, {skipped} positions non trouvees en DB.")
    print("Synchronisation terminee !")
