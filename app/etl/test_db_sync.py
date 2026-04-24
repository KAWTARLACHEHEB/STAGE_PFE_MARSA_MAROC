import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def test_db_health():
    print("--- DIAGNOSTIC SYNCHRO BASE DE DONNEES ---")
    
    db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "Kawtar@123"))
    engine = create_engine(f"mysql+mysqlconnector://root:{db_pass}@127.0.0.1/marsa_maroc_db")
    
    with engine.connect() as conn:
        # 1. Verification des Zones
        zones = conn.execute(text("SELECT nom, type_zone, max_z FROM zones_stockage")).fetchall()
        print(f"\nZones detectees ({len(zones)}) :")
        for z in zones:
            print(f"   - Zone {z[0]} : Type {z[1]} (Max Z: {z[2]})")
            
        # 2. Verification de la classification Plein/Vide
        counts = conn.execute(text("SELECT type_conteneur, COUNT(*) FROM conteneurs GROUP BY type_conteneur")).fetchall()
        print(f"\nRepartition des Conteneurs :")
        for c in counts:
            print(f"   - {c[0]} : {c[1]} unites")
            
        # 3. Verification de l'integrite des niveaux (Max 6)
        max_z = conn.execute(text("SELECT MAX(niveau_z) FROM conteneurs")).scalar()
        print(f"\nNiveau maximum en base : {max_z} (Doit etre <= 6)")
        
        # 4. Verification de la vue GOLD (Congestion)
        print(f"\nEtat de la Vue GOLD (Top 5 Congestion) :")
        gold_stats = conn.execute(text("SELECT zone, current_occupancy, congestion_rate FROM view_yard_congestion ORDER BY congestion_rate DESC LIMIT 5")).fetchall()
        for g in gold_stats:
            print(f"   - Zone {g[0]} : {g[1]} conteneurs ({g[2]}% de remplissage)")

    print("\n--- DIAGNOSTIC TERMINE ---")

if __name__ == "__main__":
    test_db_health()
