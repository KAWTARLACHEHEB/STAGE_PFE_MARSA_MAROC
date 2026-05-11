from sqlalchemy import create_engine, text
engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')
with engine.connect() as conn:
    # 1. Quelles zones spéciales sont PLEIN vs VIDE ?
    r1 = conn.execute(text("""
        SELECT nom, type_zone, types_admis, terminal 
        FROM zones_stockage 
        WHERE types_admis != 'NORMAL' AND terminal IS NOT NULL
        ORDER BY types_admis, terminal, nom
    """)).fetchall()
    print("=== ZONES SPECIALES: type_zone (PLEIN/VIDE) ===")
    for row in r1: 
        print(f"  {row[3]} | {row[0]:5s} | {row[1]:5s} | {row[2]}")
    
    # 2. Import/Export: est-ce que les zones normales ont les deux flux ?
    r2 = conn.execute(text("""
        SELECT zone, flux, COUNT(*) as cnt 
        FROM conteneurs 
        WHERE terminal='TC3' 
        GROUP BY zone, flux 
        ORDER BY zone, flux
    """)).fetchall()
    print("\n=== TC3: Distribution Flux par Zone ===")
    for row in r2[:20]: 
        print(f"  {row[0]:5s} | {row[1]:7s} | {row[2]} conteneurs")
