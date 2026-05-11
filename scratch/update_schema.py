from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

with engine.begin() as conn:
    # On ajoute les colonnes manquantes
    try:
        conn.execute(text("ALTER TABLE zones_stockage ADD COLUMN terminal VARCHAR(10)"))
    except: pass
    try:
        conn.execute(text("ALTER TABLE zones_stockage ADD COLUMN min_allee INT"))
    except: pass
    try:
        conn.execute(text("ALTER TABLE zones_stockage ADD COLUMN max_allee INT"))
    except: pass
    try:
        conn.execute(text("ALTER TABLE zones_stockage ADD COLUMN types_admis TEXT"))
    except: pass
    
    # On cree la table mouvements_pointage si elle manque
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
    
    print("Schema mis a jour !")
