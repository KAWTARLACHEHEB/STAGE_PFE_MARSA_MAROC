from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

engine = create_engine('mysql+mysqlconnector://root:Kawtar@123@127.0.0.1:3306/marsa_maroc_db')
df = pd.read_sql(text("SELECT * FROM conteneurs WHERE zone='01A' AND allee='5' AND pile='ZONE_C'"), engine)
print(df[['reference', 'zone', 'allee', 'pile', 'niveau_z', 'slot']])
