from sqlalchemy import create_engine, text

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def check_data():
    with engine.connect() as conn:
        # On regarde le Bloc AZ, Allee 100
        sql = "SELECT reference, slot, pile, niveau_z, type_conteneur FROM conteneurs WHERE zone='AZ' AND allee='100' ORDER BY pile, niveau_z"
        result = conn.execute(text(sql)).fetchall()
        print(f"Trouvé {len(result)} conteneurs dans AZ-100")
        for row in result:
            print(f"Ref: {row[0]} | Slot: {row[1]} | Pile: {row[2]} | Niveau: {row[3]}")

if __name__ == "__main__":
    check_data()
