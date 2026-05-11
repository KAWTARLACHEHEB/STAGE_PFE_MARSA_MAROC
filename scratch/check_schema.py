from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def check():
    with engine.connect() as conn:
        res = conn.execute(text("DESCRIBE conteneurs")).fetchall()
        print("Colonnes dans 'conteneurs':")
        for r in res:
            print(f"- {r[0]} ({r[1]})")

if __name__ == "__main__":
    check()
