import json
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

def import_pointages_expert():
    # 1. Configuration
    load_dotenv()
    db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    db_port = os.getenv("MYSQL_PORT", "3307")
    db_user = os.getenv("MYSQL_USER", "root")
    db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "rootpassword"))
    db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
    
    engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    # 2. Donnees de Test Expertes
    data = [
        {"conteneur": "HLBU1774325", "position": "02D57B4", "terminal": "TC3"},
        {"conteneur": "KOCU5144780", "position": "TP014C11", "terminal": "TCE"},
        {"conteneur": "UACU4753041", "position": "L008A01", "terminal": "TCE"}
    ]

    # 3. Insertion dans mouvements_pointage
    print(f"Importation experte de {len(data)} pointages...")
    try:
        with engine.connect() as conn:
            # Nettoyage pour le test
            conn.execute(text("TRUNCATE TABLE mouvements_pointage"))
            for item in data:
                conn.execute(text("""
                    INSERT INTO mouvements_pointage (conteneur, position, terminal, zone)
                    VALUES (:ref, :pos, :term, :zone)
                """), {
                    "ref": item['conteneur'],
                    "pos": item['position'],
                    "term": item['terminal'],
                    "zone": item['position'][:3] # Extraction simplifiee du bloc
                })
            conn.commit()
            print("Importation terminee avec succes !")
    except Exception as e:
        print(f"Erreur lors de l'importation : {e}")

if __name__ == "__main__":
    import_pointages_expert()
