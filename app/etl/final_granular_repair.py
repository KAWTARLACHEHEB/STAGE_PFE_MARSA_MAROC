from sqlalchemy import create_engine, text
import pandas as pd
import random

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def final_granular_repair():
    with engine.connect() as conn:
        print("[GranularRepair] Loading Referentiel and Container Data...")
        # 1. Charger le referentiel (qui contient les zones et leur capacite totale)
        df_ref = pd.read_csv('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/data/processed/referentiel_zones_FINAL.csv')
        
        # 2. Charger les conteneurs (13249)
        df_raw = pd.read_csv('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/data/raw/positions_parc_marsa_CLEAN.csv')
        
        print(f"[GranularRepair] Total Containers: {len(df_raw)}")

        # 3. Créer une liste de positions GRANULAIRES
        # Pour chaque ligne du referentiel, on genere autant de piles que necessaire
        all_spots = []
        for _, row in df_ref.iterrows():
            total_evp = int(row['CAPACITE_TOTALE_EVP'])
            limit = 4 if row['CATEGORIE_STORAGE'] == 'ZONE_PLEIN' else 6
            
            # Combien de piles de 'limit' niveaux faut-il pour loger total_evp ?
            num_piles = (total_evp // limit) + 1
            
            orig_pile = str(row['CELLULE'])
            
            for p_idx in range(num_piles):
                # On cree des noms de piles : A1, A2, A3... ou ZONE_C_1, ZONE_C_2...
                pile_name = f"{orig_pile}_{p_idx+1}" if num_piles > 1 else orig_pile
                
                for n in range(1, limit + 1):
                    all_spots.append({
                        'z': row['BLOC'],
                        'a': row['TRAVEE'],
                        'p': pile_name,
                        'n': n,
                        't': row['TERMINAL'],
                        'type': row['CATEGORIE_STORAGE'].replace('ZONE_', '')
                    })

        print(f"[GranularRepair] Generated {len(all_spots)} granular spots.")
        # On melange pour eviter de remplir tout le temps les memes blocs au debut
        random.shuffle(all_spots)

        # 4. Attribution
        updated_data = []
        for i, _ in df_raw.iterrows():
            if i < len(all_spots):
                spot = all_spots[i]
                updated_data.append({
                    "ref": f"MAR-{i:06d}",
                    "z": spot['z'], "a": spot['a'], "p": spot['p'], "n": spot['n'], "t": spot['t'], "type_c": spot['type']
                })

        # 5. Injection SQL
        print("[GranularRepair] Cleaning and Injecting...")
        conn.execute(text("TRUNCATE TABLE conteneurs"))
        
        chunk_size = 500
        for i in range(0, len(updated_data), chunk_size):
            chunk = updated_data[i:i + chunk_size]
            conn.execute(text("""
                INSERT INTO conteneurs 
                (reference, zone, allee, pile, niveau_z, terminal, type_conteneur, weight, size, departure_time, flux)
                VALUES (:ref, :z, :a, :p, :n, :t, :type_c, 20.0, '20', NOW(), 'IMPORT')
            """), chunk)
            
        conn.commit()
        print(f"[GranularRepair] DONE! {len(updated_data)} containers spread across the yard.")

if __name__ == "__main__":
    final_granular_repair()
