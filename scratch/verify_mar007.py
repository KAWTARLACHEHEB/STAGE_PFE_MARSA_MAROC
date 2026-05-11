from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def verify():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT reference, zone, allee, pile, niveau_z FROM conteneurs WHERE reference='MAR-000007'")).fetchone()
        print(f"Resultat : {res}")

if __name__ == "__main__":
    verify()
