from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def cleanup():
    with engine.connect() as conn:
        # Nettoyage des piles pour que l'IA ne genere plus de mauvais formats
        conn.execute(text("UPDATE conteneurs SET pile = 'C' WHERE pile = 'ZONE_C'"))
        conn.execute(text("UPDATE conteneurs SET pile = 'A' WHERE pile = 'ZONE_A'"))
        conn.execute(text("UPDATE conteneurs SET pile = 'B' WHERE pile = 'ZONE_B'"))
        conn.execute(text("UPDATE conteneurs SET pile = 'D' WHERE pile = 'ZONE_D'"))
        conn.commit()
        print("Nettoyage des piles effectue avec succes.")

if __name__ == "__main__":
    cleanup()
