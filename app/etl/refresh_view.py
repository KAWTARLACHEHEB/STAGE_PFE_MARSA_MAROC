import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def refresh_view():
    db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
    db_port = os.getenv("MYSQL_PORT", "3306")
    db_user = os.getenv("MYSQL_USER", "root")
    db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
    db_name = os.getenv("MYSQL_DATABASE", "marsa_maroc_db")
    
    engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
    
    sql = """
    CREATE OR REPLACE VIEW view_yard_congestion AS
    SELECT 
        z.nom,
        z.type_zone,
        z.terminal,
        z.capacite_max,
        z.max_z,
        z.types_admis,
        (SELECT COUNT(*) FROM conteneurs c WHERE c.zone = z.nom AND c.terminal = z.terminal) as current_occ,
        ((SELECT COUNT(*) FROM conteneurs c WHERE c.zone = z.nom AND c.terminal = z.terminal) / z.capacite_max * 100) as rate,
        (SELECT MIN(allee) FROM conteneurs c WHERE c.zone = z.nom AND c.terminal = z.terminal) as min_allee,
        (SELECT MAX(allee) FROM conteneurs c WHERE c.zone = z.nom AND c.terminal = z.terminal) as max_allee
    FROM zones_stockage z;
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print("✅ Vue 'view_yard_congestion' rafraîchie avec succès.")

if __name__ == "__main__":
    refresh_view()
