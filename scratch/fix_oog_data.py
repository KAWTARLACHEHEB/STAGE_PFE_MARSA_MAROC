from sqlalchemy import create_engine, text
import pandas as pd

# Connexion au MySQL local (port 3306)
engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

with engine.begin() as conn:
    print("Recherche des conteneurs OOG mal places...")
    
    # 1. Recuperer tous les OOG
    oog_query = text("SELECT container_id, zone, allee, pile, niveau_z FROM conteneurs WHERE specialite IN ('HORS_GABARIT', 'OOG')")
    oogs = conn.execute(oog_query).fetchall()
    print(f"Nombre total de conteneurs OOG : {len(oogs)}")
    
    fixed_count = 0
    for oog in oogs:
        c_id = oog[0]
        zone = oog[1]
        allee = oog[2]
        old_pile = oog[3]
        niveau = oog[4]
        
        # Verifier s'il y a d'autres conteneurs dans cette pile
        pile_query = text("SELECT COUNT(*) FROM conteneurs WHERE zone=:z AND allee=:a AND pile=:p")
        count_in_pile = conn.execute(pile_query, {"z": zone, "a": allee, "p": old_pile}).scalar()
        
        # Si le niveau n'est pas 1, OU s'il y a d'autres conteneurs avec lui
        if niveau > 1 or count_in_pile > 1:
            # FIX : On lui donne sa propre pile dediee (ex: OOG_1234) et on le met au niveau 1
            new_pile = f"OOG_{str(c_id)[-4:]}" # Utilise les 4 derniers caracteres de l'ID
            update_query = text("UPDATE conteneurs SET pile=:np, niveau_z=1 WHERE container_id=:id")
            conn.execute(update_query, {"np": new_pile, "id": c_id})
            fixed_count += 1
            
            # Reajuster les niveaux des conteneurs normaux restants dans l'ancienne pile
            rest_query = text("SELECT container_id FROM conteneurs WHERE zone=:z AND allee=:a AND pile=:p ORDER BY niveau_z ASC")
            rest = conn.execute(rest_query, {"z": zone, "a": allee, "p": old_pile}).fetchall()
            
            for i, r in enumerate(rest):
                new_z = i + 1
                conn.execute(text("UPDATE conteneurs SET niveau_z=:nz WHERE container_id=:id"), {"nz": new_z, "id": r[0]})
                
    print(f"Correction terminee ! {fixed_count} conteneurs OOG ont ete deplaces vers le sol (Niveau 1).")
    
    # 2. Mettre a jour la vue congestion
    conn.execute(text('DROP VIEW IF EXISTS view_yard_congestion'))
    conn.execute(text("""
        CREATE VIEW view_yard_congestion AS 
        SELECT 
            z.nom, 
            z.type_zone, 
            COUNT(c.container_id) as current_occ, 
            z.capacite_max, 
            z.max_z, 
            (COUNT(c.container_id)/z.capacite_max)*100 as rate, 
            z.terminal, 
            z.min_allee, 
            z.max_allee, 
            z.types_admis 
        FROM zones_stockage z 
        LEFT JOIN conteneurs c ON z.nom = c.zone AND z.terminal = c.terminal
        GROUP BY z.nom, z.type_zone, z.capacite_max, z.max_z, z.terminal, z.min_allee, z.max_allee, z.types_admis
    """))

print("Veuillez redemarrer le backend (py main.py) pour que le YardManager recharge les donnees en memoire.")
