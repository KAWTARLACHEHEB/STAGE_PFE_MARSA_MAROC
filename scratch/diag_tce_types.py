import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://root:Kawtar%40123@127.0.0.1:3306/marsa_maroc_db')

print("=== Zones Specialisees dans TCE ===")
query = "SELECT nom, types_admis FROM zones_stockage WHERE terminal = 'TCE'"
df_zones = pd.read_sql(query, engine)
special_zones = df_zones[df_zones['types_admis'].str.contains('DANGER|CITERNE|DANGEREUX', na=False, case=False)]
print(special_zones)

print("\n=== Conteneurs Speciaux dans TCE ===")
query_cont = "SELECT specialite, count(*) FROM conteneurs WHERE terminal = 'TCE' GROUP BY specialite"
print(pd.read_sql(query_cont, engine))

print("\n=== Zones des conteneurs DANGER/CITERNE dans TCE ===")
query_loc = "SELECT zone, specialite, count(*) FROM conteneurs WHERE terminal = 'TCE' AND specialite IN ('DANGER', 'CITERNE') GROUP BY zone, specialite"
print(pd.read_sql(query_loc, engine))
