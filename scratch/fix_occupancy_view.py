from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def fix_view():
    with engine.connect() as conn:
        sql = """
        CREATE OR REPLACE VIEW view_yard_congestion AS
        SELECT 
            z.nom, 
            z.type_zone, 
            COUNT(c.reference) as current_occ, 
            z.capacite_max, 
            z.max_z,
            (COUNT(c.reference) * 100.0 / z.capacite_max) as rate,
            z.terminal,
            z.min_allee,
            z.max_allee,
            z.types_admis
        FROM zones_stockage z
        LEFT JOIN conteneurs c ON z.nom = c.zone AND z.terminal = c.terminal
        GROUP BY z.nom, z.terminal
        """
        conn.execute(text(sql))
        conn.commit()
        print("View FIXED with floating point math.")

if __name__ == "__main__":
    fix_view()
