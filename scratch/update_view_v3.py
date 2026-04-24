import sqlalchemy
from sqlalchemy import text
engine = sqlalchemy.create_engine('mysql+mysqlconnector://root:rootpassword@127.0.0.1:3307/marsa_maroc_db')
with engine.connect() as conn:
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
    conn.commit()
print('Vue SQL mise a jour avec types admis.')
