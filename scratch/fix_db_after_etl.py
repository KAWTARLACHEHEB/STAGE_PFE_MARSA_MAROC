from sqlalchemy import create_engine, text

# Connexion au MySQL local (port 3306)
engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

with engine.begin() as conn:
    # 1. Vérifier l'état actuel
    result = conn.execute(text("SELECT COUNT(*) as cnt FROM conteneurs"))
    cnt = result.fetchone()[0]
    print(f"[DB] Conteneurs en base : {cnt}")
    
    # 2. Vérifier les nouvelles colonnes
    try:
        result = conn.execute(text("SELECT flux, statut_import, navire_id, pod FROM conteneurs LIMIT 3"))
        rows = result.fetchall()
        print(f"[DB] Nouvelles colonnes OK : {[dict(r._mapping) for r in rows]}")
    except Exception as e:
        print(f"[DB] ERREUR colonnes manquantes : {e}")
        print("[DB] Relancez le pipeline ETL (python app/etl/pipeline.py)")
    
    # 3. Vérifier les zones_stockage
    result = conn.execute(text("SELECT COUNT(*) as cnt FROM zones_stockage"))
    zcnt = result.fetchone()[0]
    print(f"[DB] Zones stockage en base : {zcnt}")
    
    # 4. Recréer la vue view_yard_congestion (CRITIQUE)
    print("[DB] Recréation de la vue view_yard_congestion...")
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
    print("[DB] Vue view_yard_congestion recréée avec succès !")
    
    # 5. Recréer la table historique si manquante
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
    
    # 6. Recréer la table pointages si manquante
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
    
    # 7. Vérification finale
    result = conn.execute(text("SELECT terminal, COUNT(*) as cnt FROM conteneurs GROUP BY terminal"))
    for row in result:
        print(f"[DB] Terminal {row[0]} : {row[1]} conteneurs")
    
    result = conn.execute(text("SELECT terminal, COUNT(*) as cnt FROM zones_stockage GROUP BY terminal"))
    for row in result:
        print(f"[DB] Zones terminal {row[0]} : {row[1]} zones")

    result = conn.execute(text("SELECT nom, current_occ, rate, terminal FROM view_yard_congestion LIMIT 5"))
    for row in result:
        print(f"[DB] Vue OK - Zone {row[0]} : {row[1]} conteneurs, {row[3]} ({row[2]:.1f}%)")

print("\n[DB] Réparation terminée avec succès ! Redémarrez le backend.")
