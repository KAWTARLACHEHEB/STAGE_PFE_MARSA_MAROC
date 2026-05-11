import pandas as pd
import numpy as np
import os
import random
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class MarsaETL:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.processed_file = self.base_dir / "data" / "processed" / "positions_normalisees_marsa.csv"
        
        db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
        db_port = os.getenv("MYSQL_PORT", "3306")
        db_user = os.getenv("MYSQL_USER", "root")
        db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
        db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
        self.engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    def prepare_db(self):
        """S'assure que la table possède les colonnes nécessaires."""
        cols_to_add = {
            'type_iso_detail': 'TEXT',
            'nom_navire': 'TEXT',
            'pod': 'TEXT'
        }
        with self.engine.connect() as conn:
            for col, dtype in cols_to_add.items():
                try:
                    conn.execute(text(f"ALTER TABLE conteneurs ADD COLUMN {col} {dtype}"))
                    print(f"[DB] Colonne {col} ajoutée.")
                except:
                    pass # Déjà existante
            conn.commit()

    def run_pipeline(self):
        print(f"[{datetime.now()}] Démarrage du Pipeline 'Système Réel'...")
        self.prepare_db()
        
        try:
            if not self.processed_file.exists():
                print(f"Erreur : Le fichier {self.processed_file} n'existe pas.")
                return False

            # Lecture du dataset normalisé (Silver)
            df = pd.read_csv(self.processed_file)
            print(f"Chargement de {len(df)} conteneurs normalisés...")

            # Préparation des données SQL (Gold)
            df_sql = pd.DataFrame()
            df_sql['container_id'] = [f"MAR-{i+1:06d}" for i in range(len(df))]
            df_sql['reference'] = df_sql['container_id']
            df_sql['terminal'] = df['TERMINAL']
            df_sql['zone'] = df['BLOC']
            df_sql['allee'] = df['TRAVEE']
            df_sql['pile'] = df['CELLULE']
            df_sql['niveau_z'] = df['NIVEAU']
            df_sql['type_conteneur'] = df['TYPE_ZONE']
            df_sql['type_iso_detail'] = df['TYPE_ISO_DETAIL']
            df_sql['flux'] = df['FLUX']
            df_sql['statut_import'] = df['STATUS_DOUANE']
            df_sql['nom_navire'] = df['NOM_NAVIRE']
            df_sql['pod'] = df['POD']
            
            # Attributs techniques additionnels
            df_sql['size'] = [random.choice(['20', '40']) for _ in range(len(df))]
            df_sql['weight'] = [random.uniform(18.0, 30.0) if t == 'PLEIN' else random.uniform(2.0, 5.0) for t in df['TYPE_ZONE']]
            df_sql['specialite'] = df['TYPE_ISO_DETAIL'].apply(lambda x: 'OOG' if 'HORS GABARIT' in str(x) else 'NORMAL')
            
            # Dates de départ réalistes (+3 à +10 jours)
            df_sql['departure_time'] = [datetime.now() + timedelta(days=random.randint(3,10)) for _ in range(len(df))]
            
            # Construction du SLOT unique
            df_sql['slot'] = df_sql.apply(lambda r: f"{r['terminal']}-{r['zone']}-{r['allee']}-{r['pile']}-N{int(r['niveau_z']):02d}", axis=1)

            # Mise à jour des zones de stockage (Referentiel)
            with self.engine.connect() as conn:
                unique_zones = df.groupby(['BLOC', 'TYPE_ZONE', 'TERMINAL']).size().reset_index()
                for _, row in unique_zones.iterrows():
                    zmax = 6 if row['TYPE_ZONE'] == 'VIDE' else (3 if row['TERMINAL'] == 'TCE' else 5)
                    conn.execute(text("""
                        INSERT INTO zones_stockage (nom, type_zone, capacite_max, max_z, terminal, types_admis) 
                        VALUES (:nom, :type, 2000, :zmax, :term, 'TOUS')
                        ON DUPLICATE KEY UPDATE type_zone=:type, max_z=:zmax, terminal=:term
                    """), {
                        "nom": row['BLOC'], "type": row['TYPE_ZONE'], "zmax": zmax, "term": row['TERMINAL']
                    })
                conn.commit()

            # Injection finale
            df_sql.to_sql('conteneurs', con=self.engine, if_exists='replace', index=False)
            
            print(f"[{datetime.now()}] Pipeline Terminé. {len(df_sql)} conteneurs en ligne sur le dashboard.")
            return True
            
        except Exception as e:
            print(f"Erreur Pipeline : {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    MarsaETL().run_pipeline()
