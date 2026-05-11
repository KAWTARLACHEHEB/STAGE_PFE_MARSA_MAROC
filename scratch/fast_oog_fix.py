from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')
with engine.begin() as conn:
    print("Execution de la mise a jour SQL rapide...")
    conn.execute(text("UPDATE conteneurs SET pile = CONCAT('OOG_', RIGHT(container_id, 4)), niveau_z = 1 WHERE specialite IN ('OOG', 'HORS_GABARIT')"))
    
    print("Mise a jour de la vue SQL...")
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

print("OOG fix complete.")
