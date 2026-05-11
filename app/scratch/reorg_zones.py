import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

def reorg_zones():
    p = quote_plus("Kawtar@123")
    engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")
    
    with engine.begin() as conn:
        # 1. Remettre tout à Normal par défaut
        conn.execute(text("UPDATE zones_stockage SET types_admis = 'NORMAL'"))
        
        # 2. Assigner les blocs spécifiques
        conn.execute(text("UPDATE zones_stockage SET types_admis = 'FRIGO' WHERE nom LIKE '02A%' OR nom LIKE '02B%'"))
        conn.execute(text("UPDATE zones_stockage SET types_admis = 'DANGEREUX' WHERE nom LIKE '02C%' OR nom LIKE '02D%'"))
        conn.execute(text("UPDATE zones_stockage SET types_admis = 'HORS_GABARIT' WHERE nom LIKE '02E%' OR nom LIKE '02F%'"))
        conn.execute(text("UPDATE zones_stockage SET types_admis = 'CITERNE' WHERE nom LIKE '02G%' OR nom LIKE '02H%'"))
        
        print("Zones reorganisees avec succes (Strict Mode).")

if __name__ == "__main__":
    reorg_zones()
