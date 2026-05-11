from sqlalchemy import create_engine, text
engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')
with engine.connect() as conn:
    r = conn.execute(text("SELECT terminal, COUNT(*) FROM conteneurs GROUP BY terminal")).fetchall()
    print(f"Terminaux dans la DB : {r}")
    
    r2 = conn.execute(text("SELECT zone, flux, COUNT(*) FROM conteneurs WHERE terminal='TC3' GROUP BY zone, flux")).fetchall()
    print(f"Distribution Flux dans TC3 : {r2[:10]}")
    
    r3 = conn.execute(text("SELECT flux, COUNT(*) FROM conteneurs WHERE terminal='TC3' GROUP BY flux")).fetchall()
    print(f"Flux totaux TC3 : {r3}")
