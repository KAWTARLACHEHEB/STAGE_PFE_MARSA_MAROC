from sqlalchemy import create_engine, text

# Utilisation du port 3306 (MySQL local qui contient les 13k conteneurs)
engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

with engine.begin() as conn:
    # 1. Mise a jour de la vue
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
        LEFT JOIN conteneurs c ON z.nom = c.zone 
        GROUP BY z.nom, z.type_zone, z.capacite_max, z.max_z, z.terminal, z.min_allee, z.max_allee, z.types_admis
    """))
    
    # 2. Creation de la table historique si manquante
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS historique_mouvements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            reference VARCHAR(50),
            action VARCHAR(20),
            slot VARCHAR(20),
            terminal VARCHAR(10),
            status VARCHAR(20),
            horodatage TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 3. Creation de la table pointages si manquante (utilisée par la recherche universelle)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS mouvements_pointage (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conteneur VARCHAR(20),
            position VARCHAR(20),
            terminal VARCHAR(10),
            zone VARCHAR(10),
            date_heure TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

print("Vues et tables auxiliaires mises a jour sur le port 3306 !")
