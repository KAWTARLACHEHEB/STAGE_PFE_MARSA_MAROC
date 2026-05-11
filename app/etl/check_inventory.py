import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def check_inventory():
    p = quote_plus("Kawtar@123")
    engine = create_engine(f"mysql+mysqlconnector://root:{p}@127.0.0.1:3306/marsa_maroc_db")
    
    print("--- INVENTAIRE PAR ZONE (Top 10) ---")
    query = "SELECT terminal, zone, COUNT(*) as total FROM conteneurs GROUP BY terminal, zone ORDER BY total DESC LIMIT 10"
    df = pd.read_sql(query, engine)
    print(df)
    
    print("\n--- VERIFICATION SPECIFIQUE BLOC AP ---")
    query_ap = "SELECT terminal, zone, COUNT(*) as total FROM conteneurs WHERE zone = 'AP' GROUP BY terminal, zone"
    df_ap = pd.read_sql(query_ap, engine)
    if df_ap.empty:
        print("❌ Le BLOC AP est VIDE dans la base de données.")
    else:
        print(df_ap)

if __name__ == "__main__":
    check_inventory()
