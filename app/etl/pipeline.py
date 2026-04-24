import pandas as pd
import numpy as np
import os
import random
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from repair_marsa_data import repair_marsa_pipeline
from create_referentiel import create_marsa_referentiel

load_dotenv()

class MarsaETL:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        
        db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
        db_port = os.getenv("MYSQL_PORT", "3307")
        db_user = os.getenv("MYSQL_USER", "root")
        db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "rootpassword"))
        db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
        self.engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    def generate_realistic_departure(self):
        days_ahead = random.randint(1, 10)
        return datetime.now() + timedelta(days=days_ahead)

    def run_pipeline(self):
        print(f"[{datetime.now()}] Demarrage du Pipeline avec REFERENTIEL...")
        
        try:
            # 1. Reparation Chirurgicale
            input_csv = self.raw_dir / "positions_parc_marsa_CLEAN.csv"
            repaired_csv = self.processed_dir / "positions_finales_reparees.csv"
            if not repair_marsa_pipeline(str(input_csv), str(repaired_csv)):
                return False

            # 2. Creation du REFERENTIEL STRATEGIQUE (Nouveaute)
            print("[Gold] Generation du Referentiel des Zones...")
            ref_csv = self.processed_dir / "referentiel_zones_FINAL.csv"
            create_marsa_referentiel(str(repaired_csv), str(ref_csv))

            # 3. Chargement et Enrichissement
            df_pos = pd.read_csv(repaired_csv)
            df_ref = pd.read_csv(ref_csv)
            
            # On fusionne l'inventaire avec le referentiel pour recuperer CATEGORIE_STORAGE et TYPES_ADMIS
            df_pos = pd.merge(df_pos, df_ref[['BLOC', 'TRAVEE', 'CELLULE', 'CATEGORIE_STORAGE', 'TYPES_ADMIS']], on=['BLOC', 'TRAVEE', 'CELLULE'], how='left')
            
            hybrid_path = self.raw_dir / "hybrid_snapshot_1k_v2.csv"
            df_log = pd.read_csv(hybrid_path) if hybrid_path.exists() else pd.DataFrame()
            
            # Harmonisation
            df_pos['slot_key'] = df_pos['BLOC'] + "-" + df_pos['TRAVEE'].astype(str) + "-" + df_pos['CELLULE'] + "-" + df_pos['NIVEAU'].astype(int).apply(lambda x: f"{x:02d}")
            if not df_log.empty:
                df_log['slot_key'] = df_log['slot']

            # Fusion et Generation
            df_merged = pd.merge(df_pos, df_log[['slot_key', 'size', 'weight', 'departure_time', 'type']], on='slot_key', how='left')
            
            # Classification par defaut : On utilise la categorie du referentiel
            # (On enleve le prefixe 'ZONE_' pour le formatage DB)
            df_merged['TYPE_ZONE'] = df_merged['CATEGORIE_STORAGE'].fillna('ZONE_VIDE').str.replace('ZONE_', '', regex=False)
            
            # Remplissage realiste
            is_plein = (df_merged['TYPE_ZONE'] == 'PLEIN') & (df_merged['weight'].isna())
            df_merged.loc[is_plein, 'weight'] = [random.uniform(18.0, 30.0) for _ in range(is_plein.sum())]
            df_merged.loc[is_plein, 'size'] = [random.choice([20, 40]) for _ in range(is_plein.sum())]
            
            is_vide = (df_merged['TYPE_ZONE'] == 'VIDE') & (df_merged['weight'].isna())
            df_merged.loc[is_vide, 'weight'] = [random.uniform(2.0, 5.0) for _ in range(is_vide.sum())]
            df_merged.loc[is_vide, 'size'] = [random.choice([20, 40]) for _ in range(is_vide.sum())]
            
            mask_no_date = df_merged['departure_time'].isna()
            df_merged.loc[mask_no_date, 'departure_time'] = [self.generate_realistic_departure().isoformat() for _ in range(mask_no_date.sum())]
            # Attribution des types (Normal, Frigo, Danger, OOG) en fonction des zones
            def assign_spec(row):
                # Si deja defini par l'historique, on garde
                if not pd.isna(row['type']) and row['type'] not in ['PLEIN', 'VIDE']: return row['type']
                
                admitted = str(row['TYPES_ADMIS']).upper()
                import random
                if "FRIGO" in admitted and random.random() < 0.4: return "FRIGO"
                if "DANGER" in admitted and random.random() < 0.3: return "DANGER"
                if "HORS_GABARIT" in admitted and random.random() < 0.2: return "OOG"
                return "NORMAL"

            df_merged['type'] = df_merged.apply(assign_spec, axis=1)

            # 4. Synchronisation SQL
            print("[Gold] Synchronisation avec la Base de Donnees...")
            df_sql = pd.DataFrame()
            df_sql['container_id'] = [f"MAR-{i:06d}" for i in range(len(df_merged))]
            df_sql['reference'] = df_sql['container_id']
            df_sql['terminal'] = df_merged['TERMINAL']
            df_sql['size'] = df_merged['size'].astype(str)
            df_sql['weight'] = df_merged['weight']
            df_sql['type_conteneur'] = df_merged['TYPE_ZONE']
            df_sql['specialite'] = df_merged['type']
            df_sql['zone'] = df_merged['BLOC']
            df_sql['allee'] = df_merged['TRAVEE']
            df_sql['pile'] = df_merged['CELLULE']
            df_sql['niveau_z'] = df_merged['NIVEAU']
            df_sql['slot'] = df_merged['slot_key']
            df_sql['departure_time'] = pd.to_datetime(df_merged['departure_time'], format='ISO8601')

            with self.engine.connect() as conn:
                # Sync des Zones (Enrichies par le referentiel)
                unique_zones = df_merged.groupby(['BLOC', 'TYPE_ZONE', 'TERMINAL']).agg({
                    'TRAVEE': ['min', 'max'],
                    'TYPES_ADMIS': 'first'
                }).reset_index()
                unique_zones.columns = ['nom', 'type', 'terminal', 'min_a', 'max_a', 'types_admis']

                for _, row in unique_zones.iterrows():
                    z_max = 4 if row['type'] == 'PLEIN' else 6
                    conn.execute(text("""
                        INSERT INTO zones_stockage (nom, type_zone, capacite_max, max_z, terminal, min_allee, max_allee, types_admis) 
                        VALUES (:nom, :type, :cap, :zmax, :term, :mina, :maxa, :t_admis)
                        ON DUPLICATE KEY UPDATE type_zone=:type, max_z=:zmax, terminal=:term, min_allee=:mina, max_allee=:maxa, types_admis=:t_admis
                    """), {
                        "nom": row['nom'], "type": row['type'], "cap": 2000, 
                        "zmax": z_max, "term": row['terminal'],
                        "mina": row['min_a'], "maxa": row['max_a'],
                        "t_admis": row['types_admis']
                    })
                conn.commit()

            df_sql.to_sql('conteneurs', con=self.engine, if_exists='replace', index=False)
            print(f"[{datetime.now()}] Pipeline avec REFERENTIEL termine avec succes !")
            return True
            
        except Exception as e:
            print(f"Erreur : {str(e)}")
            return False

if __name__ == "__main__":
    MarsaETL().run_pipeline()
