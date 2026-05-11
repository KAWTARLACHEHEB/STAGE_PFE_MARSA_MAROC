from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

def check_special_zones():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT types_admis, type_zone, count(*) as total FROM zones_stockage WHERE type_zone = 'PLEIN' GROUP BY types_admis"))
        df = pd.DataFrame(res.fetchall(), columns=['types_admis', 'type_zone', 'total'])
        print(df)

if __name__ == "__main__":
    check_special_zones()
