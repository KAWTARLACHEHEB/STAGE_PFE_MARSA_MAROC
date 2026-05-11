from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def check_special_distribution():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT flux, specialite, count(*) as total FROM conteneurs GROUP BY flux, specialite"))
        df = pd.DataFrame(res.fetchall(), columns=['flux', 'specialite', 'total'])
        print(df)

if __name__ == "__main__":
    check_special_distribution()
