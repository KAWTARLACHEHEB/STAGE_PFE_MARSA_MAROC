import sys
import os
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

db_host = "127.0.0.1"
db_port = "3306"
db_user = "root"
db_pass = "Kawtar@123"
db_name = "marsa_maroc_db"

engine = create_engine(f"mysql+mysqlconnector://{db_user}:{quote_plus(db_pass)}@{db_host}:{db_port}/{db_name}")

with engine.connect() as conn:
    df = pd.read_sql(text("SELECT zone, allee, pile, niveau_z FROM conteneurs WHERE terminal = 'TC3'"), conn)
    
    # Sort and group
    df = df.sort_values(['zone', 'allee', 'pile', 'niveau_z'])
    
    holes = []
    for (z, a, p), group in df.groupby(['zone', 'allee', 'pile']):
        levels = sorted(group['niveau_z'].tolist())
        if not levels: continue
        max_l = max(levels)
        expected = list(range(1, max_l + 1))
        missing = [l for l in expected if l not in levels]
        if missing:
            holes.append(f"Zone {z}, Allee {a}, Pile {p}: Missing levels {missing} (Max level {max_l})")
            
    if holes:
        print("\n".join(holes[:20]))
        print(f"\nTotal stacks with holes: {len(holes)}")
    else:
        print("No holes found in stacks.")
