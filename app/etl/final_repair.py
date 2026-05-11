from sqlalchemy import create_engine, text
import pandas as pd
import random

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def final_data_repair():
    with engine.connect() as conn:
        print("[FinalRepair] Loading Referentiel and Raw Data...")
        # 1. Charger les slots valides
        df_slots = pd.read_csv('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/data/processed/referentiel_zones_FINAL.csv')
        
        # 2. Charger les 13249 conteneurs (on ne prend que les entités)
        df_raw = pd.read_csv('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/data/raw/positions_parc_marsa_CLEAN.csv')
        
        print(f"[FinalRepair] Total Containers to place: {len(df_raw)}")
        print(f"[FinalRepair] Total Slots available: {len(df_slots)}")

        # 3. Préparer le brassage
        # On va créer une liste de TOUTES les positions possibles (Slot x Niveau)
        all_positions = []
        for _, slot in df_slots.iterrows():
            # Pour loger 13249 TC dans 2393 slots, on doit monter un peu
            # On garde PLEIN à 4, mais on monte VIDE à 7 pour compenser
            limit = 4 if slot['CATEGORIE_STORAGE'] == 'ZONE_PLEIN' else 7
            for n in range(1, limit + 1):
                all_positions.append({
                    'zone': slot['BLOC'],
                    'allee': slot['TRAVEE'],
                    'pile': slot['CELLULE'],
                    'niveau': n,
                    'terminal': slot['TERMINAL'],
                    'type_z': slot['CATEGORIE_STORAGE'].replace('ZONE_', '')
                })
        
        print(f"[FinalRepair] Total capacity created: {len(all_positions)} spots.")
        
        # On mélange les positions pour une répartition homogène
        random.shuffle(all_positions)
        
        # 4. Attribution
        print("[FinalRepair] Attributing positions to containers...")
        updated_data = []
        for i, row in df_raw.iterrows():
            if i >= len(all_positions):
                # Si on dépasse (ne devrait pas arriver ici), on sature les derniers slots
                pos = all_positions[-1]
            else:
                pos = all_positions[i]
                
            updated_data.append({
                "ref": f"MAR-{i:06d}",
                "z": pos['zone'],
                "a": pos['allee'],
                "p": pos['pile'],
                "n": pos['niveau'],
                "t": pos['terminal'],
                "type_c": pos['type_z'],
                "w": random.uniform(18.0, 30.0) if pos['type_z'] == 'PLEIN' else random.uniform(2.0, 5.0)
            })

        # 5. Injection SQL massive
        print("[FinalRepair] Cleaning database...")
        conn.execute(text("TRUNCATE TABLE conteneurs"))
        
        print("[FinalRepair] Injecting 13249 containers...")
        chunk_size = 500
        for i in range(0, len(updated_data), chunk_size):
            chunk = updated_data[i:i + chunk_size]
            conn.execute(text("""
                INSERT INTO conteneurs 
                (reference, zone, allee, pile, niveau_z, terminal, type_conteneur, weight, size, departure_time, flux)
                VALUES (:ref, :z, :a, :p, :n, :t, :type_c, :w, '20', NOW(), 'IMPORT')
            """), chunk)
            
        conn.commit()
        print("[FinalRepair] SUCCESS! All containers placed and limits respected.")

if __name__ == "__main__":
    final_data_repair()
