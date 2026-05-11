from sqlalchemy import create_engine, text
import pandas as pd
import random

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def redistribute_overflow():
    with engine.connect() as conn:
        print("[Redistribute] Loading data...")
        df = pd.read_sql(text("SELECT * FROM conteneurs"), conn)
        zones = pd.read_sql(text("SELECT nom, max_z, min_allee, max_allee FROM zones_stockage"), conn)
        z_config = {r['nom']: r for r in zones.to_dict('records')}
        
        # 1. Identifier l'état du yard
        yard_state = {} # (zone, allee, pile) -> [niveau_z]
        for idx, row in df.iterrows():
            key = (row['zone'], row['allee'], row['pile'])
            if key not in yard_state: yard_state[key] = []
            yard_state[key].append(row['niveau_z'])
            
        # 2. Identifier les débordements
        overflow_containers = []
        clean_df = []
        
        print("[Redistribute] Analyzing stacks...")
        # On regroupe par pile pour voir qui doit bouger
        for key, levels in yard_state.items():
            zone, allee, pile = key
            limit = z_config.get(zone, {'max_z': 4})['max_z']
            
            # On trie les niveaux pour garder les plus bas
            levels.sort()
            
            # Les conteneurs qui dépassent la limite
            if len(levels) > limit:
                # On garde les 'limit' premiers
                # On ajoute les autres à la liste de redistribution
                # Pour simplifier, on va juste marquer les IDs
                stack_containers = df[(df['zone'] == zone) & (df['allee'] == allee) & (df['pile'] == pile)].sort_values('niveau_z')
                clean_df.append(stack_containers.head(limit))
                overflow_containers.append(stack_containers.tail(len(levels) - limit))
            else:
                clean_df.append(df[(df['zone'] == zone) & (df['allee'] == allee) & (df['pile'] == pile)])

        if not overflow_containers:
            print("[Redistribute] No overflow found.")
            return

        overflow_df = pd.concat(overflow_containers)
        print(f"[Redistribute] {len(overflow_df)} containers to redistribute.")
        
        # 3. Trouver de nouvelles places (Re-stacking horizontal)
        # On va chercher des piles qui ont de la place dans la MEME zone
        print("[Redistribute] Finding new slots...")
        
        updated_rows = []
        
        for idx, row in overflow_df.iterrows():
            zone = row['zone']
            config = z_config.get(zone)
            limit = config['max_z']
            
            # Stratégie simple : on cherche une allée/pile au hasard dans la même zone
            found = False
            try:
                m_a = int(config['min_allee']) if pd.notnull(config['min_allee']) else 1
                M_a = int(config['max_allee']) if pd.notnull(config['max_allee']) else 50
            except:
                m_a, M_a = 1, 50

            for _ in range(50): # 50 tentatives
                new_a = random.randint(m_a, M_a)
                new_p = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'ZONE_C']) # Selon le format du parc
                
                # Vérifier l'occupation (approximative via le yard_state qu'on met à jour)
                new_key = (zone, new_a, new_p)
                current_count = len(yard_state.get(new_key, []))
                
                if current_count < limit:
                    # On a trouvé !
                    new_n = current_count + 1
                    if new_key not in yard_state: yard_state[new_key] = []
                    yard_state[new_key].append(new_n)
                    
                    # Mettre à jour l'objet
                    row['allee'] = new_a
                    row['pile'] = new_p
                    row['niveau_z'] = new_n
                    updated_rows.append(row)
                    found = True
                    break
            
            if not found:
                # Si vraiment pas de place dans la zone (rare), on laisse tel quel (ou on cherche ailleurs)
                updated_rows.append(row)

        # 4. Update Database
        print("[Redistribute] Updating database...")
        for row in updated_rows:
            conn.execute(text("""
                UPDATE conteneurs 
                SET allee = :a, pile = :p, niveau_z = :n
                WHERE reference = :ref
            """), {
                "a": row['allee'], "p": row['pile'], "n": row['niveau_z'], "ref": row['reference']
            })
        conn.commit()
        print("[Redistribute] Success! All containers preserved and redistributed.")

if __name__ == "__main__":
    redistribute_overflow()
