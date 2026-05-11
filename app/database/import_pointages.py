import json
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

def import_pointages():
    # 1. Configuration
    load_dotenv()
    base_dir = Path(__file__).resolve().parent.parent.parent
    json_path = base_dir / "data" / "raw" / "pointages_reels.json"
    
    db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    db_port = os.getenv("MYSQL_PORT", "3307")
    db_user = os.getenv("MYSQL_USER", "root")
    db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "rootpassword"))
    db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
    
    engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    if not json_path.exists():
        print(f"Erreur: Fichier {json_path} non trouve")
        return

    # 2. Lecture du JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    # 3. Insertion dans MySQL
    print(f"Importation de {len(data)} pointages...")
    try:
        with engine.connect() as conn:
            for item in data:
                conn.execute(text("""
                    INSERT INTO mouvements_actuels (reference, position_brute, terminal)
                    VALUES (:ref, :pos, :term)
                """), {
                    "ref": item['reference'],
                    "pos": item['position_brute'],
                    "term": item['terminal']
                })
            conn.commit()
            print("Importation terminee avec succes !")
    except Exception as e:
        print(f"Erreur lors de l'importation : {e}")

if __name__ == "__main__":
    import_pointages()
