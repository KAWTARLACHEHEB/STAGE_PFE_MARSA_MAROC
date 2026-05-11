import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def soft_oog_fix():
    print("Chargement des donnees...")
    df = pd.read_sql("SELECT * FROM conteneurs", engine)
    df_zones = pd.read_sql("SELECT nom, max_z FROM zones_stockage", engine)
    zone_limits = dict(zip(df_zones['nom'], df_zones['max_z']))
    
    print(f"Traitement de {len(df)} conteneurs...")
    
    # 1. Identifier les OOG
    oog_mask = df['specialite'].isin(['OOG', 'HORS_GABARIT', 'HORS GABARIT'])
    df_oog = df[oog_mask].copy()
    
    # 2. Forcer les OOG au niveau 1
    df.loc[oog_mask, 'niveau_z'] = 1
    
    # 3. Trouver les piles avec OOG
    oog_piles = df_oog[['zone', 'allee', 'pile']].drop_duplicates()
    
    total_moved = 0
    
    for _, pile_info in oog_piles.iterrows():
        z, a, p = pile_info['zone'], pile_info['allee'], pile_info['pile']
        
        # Conteneurs dans cette pile qui ne sont pas OOG
        others_mask = (df['zone'] == z) & (df['allee'] == a) & (df['pile'] == p) & (~df['specialite'].isin(['OOG', 'HORS_GABARIT', 'HORS GABARIT']))
        others = df[others_mask]
        
        if len(others) > 0:
            # On doit deplacer ces conteneurs
            # On cherche une pile voisine dans la meme zone
            found_space = False
            for offset in range(1, 20): # On cherche jusqu'a 20 piles plus loin
                for direction in [1, -1]:
                    new_p = chr(ord(p) + offset * direction) if len(p) == 1 else p # Simplifie pour les piles alphabetiques
                    if not ('A' <= new_p <= 'Z'): continue
                    
                    # Verifier si cette nouvelle pile a de la place et PAS d'OOG
                    new_pile_mask = (df['zone'] == z) & (df['allee'] == a) & (df['pile'] == new_p)
                    new_pile_cont = df[new_pile_mask]
                    
                    has_oog = any(new_pile_cont['specialite'].isin(['OOG', 'HORS_GABARIT', 'HORS GABARIT']))
                    current_count = len(new_pile_cont)
                    max_z = zone_limits.get(z, 4)
                    
                    if not has_oog and current_count < max_z:
                        # On deplace UN conteneur ici
                        idx_to_move = others.index[0]
                        df.at[idx_to_move, 'pile'] = new_p
                        df.at[idx_to_move, 'niveau_z'] = current_count + 1
                        df.at[idx_to_move, 'slot'] = f"{z}-{a}-{new_p}-N{int(current_count + 1)}"
                        
                        # Mettre a jour others pour le prochain tour si besoin
                        others = others.drop(idx_to_move)
                        total_moved += 1
                        if len(others) == 0:
                            found_space = True
                            break
                if found_space: break
                
    print(f"Redistribution terminee. {total_moved} conteneurs ont ete deplaces pour liberer les OOG.")
    
    # 4. Sauvegarde
    df.to_sql('conteneurs', con=engine, if_exists='replace', index=False)
    print("Base de donnees mise a jour avec 100% des donnees preservees.")

if __name__ == "__main__":
    soft_oog_fix()
