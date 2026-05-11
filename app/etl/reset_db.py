import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def reset_and_load_gold():
    db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    db_port = os.getenv("MYSQL_PORT", "3306")
    db_user = os.getenv("MYSQL_USER", "root")
    db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
    db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
    engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    print("1. Reconstruction des tables (Clean Slate)...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS conteneurs"))
        conn.execute(text("DROP TABLE IF EXISTS zones_stockage"))
        
        # Table Conteneurs (Format Complet)
        conn.execute(text("""
            CREATE TABLE conteneurs (
                container_id VARCHAR(50) PRIMARY KEY,
                reference VARCHAR(50),
                terminal VARCHAR(10),
                zone VARCHAR(20),
                allee INT,
                pile VARCHAR(10),
                niveau_z INT,
                type_conteneur VARCHAR(20),
                type_iso_detail TEXT,
                flux VARCHAR(20),
                status_douane TEXT,
                nom_navire TEXT,
                pod TEXT,
                size VARCHAR(10),
                weight DOUBLE,
                specialite VARCHAR(20),
                departure_time DATETIME,
                slot TEXT
            )
        """))
        
        # Table Zones (Referentiel)
        conn.execute(text("""
            CREATE TABLE zones_stockage (
                nom VARCHAR(20),
                terminal VARCHAR(10),
                type_zone VARCHAR(20),
                capacite_max INT DEFAULT 2000,
                max_z INT DEFAULT 6,
                types_admis TEXT,
                PRIMARY KEY (nom, terminal)
            )
        """))
        conn.commit()

    print("2. Chargement du dataset normalise (13 249 TC)...")
    csv_path = r"c:\Users\hp\Desktop\STAGE_PFE_MARSA_MAROC\data\processed\positions_normalisees_marsa.csv"
    df = pd.read_csv(csv_path)
    
    # Pre-processing pour MySQL
    df['TERMINAL'] = df['TERMINAL'].str.strip().str.upper()
    df['BLOC'] = df['BLOC'].astype(str).str.strip().str.upper()
    df['CELLULE'] = df['CELLULE'].astype(str).str.strip().str.upper()
    
    # Re-empilage et data mapping
    df_sql = pd.DataFrame()
    df_sql['container_id'] = [f"MAR-{i+1:06d}" for i in range(len(df))]
    df_sql['reference'] = df_sql['container_id']
    df_sql['terminal'] = df['TERMINAL']
    df_sql['zone'] = df['BLOC']
    df_sql['allee'] = df['TRAVEE'].astype(int)
    df_sql['pile'] = df['CELLULE']
    df_sql['niveau_z'] = df['NIVEAU'].astype(int)
    df_sql['type_conteneur'] = df['TYPE_ZONE']
    df_sql['type_iso_detail'] = df['TYPE_ISO_DETAIL']
    df_sql['flux'] = df['FLUX']
    df_sql['status_douane'] = df['STATUS_DOUANE']
    df_sql['nom_navire'] = df['NOM_NAVIRE']
    df_sql['pod'] = df['POD']
    df_sql['size'] = '20'
    df_sql['weight'] = 22000.0
    df_sql['specialite'] = df['TYPE_ISO_DETAIL'].apply(lambda x: 'OOG' if 'HORS GABARIT' in str(x) else 'NORMAL')
    df_sql['departure_time'] = pd.to_datetime('2026-06-01')
    df_sql['slot'] = df_sql.apply(lambda r: f"{r['terminal']}-{r['zone']}-{r['allee']}-{r['pile']}-N{int(r['niveau_z']):02d}", axis=1)

    df_sql.to_sql('conteneurs', con=engine, if_exists='append', index=False)

    print("3. Synchronisation des zones de stockage...")
    unique_zones = df.groupby(['BLOC', 'TYPE_ZONE', 'TERMINAL']).size().reset_index()
    with engine.connect() as conn:
        for _, row in unique_zones.iterrows():
            zmax = 6 if row['TYPE_ZONE'] == 'VIDE' else (3 if row['TERMINAL'] == 'TCE' else 5)
            conn.execute(text("""
                INSERT INTO zones_stockage (nom, terminal, type_zone, max_z, types_admis)
                VALUES (:nom, :term, :type, :zmax, 'TOUS')
            """), {"nom": row['BLOC'], "term": row['TERMINAL'], "type": row['TYPE_ZONE'], "zmax": zmax})
        conn.commit()

    print(f"✅ Base de donnes prete et compatible : {len(df_sql)} conteneurs charges.")

if __name__ == "__main__":
    reset_and_load_gold()
