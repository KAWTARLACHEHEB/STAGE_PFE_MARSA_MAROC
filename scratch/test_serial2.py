import sys
import os
sys.path.append('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/app')
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus
import json

db_host = "127.0.0.1"
db_port = "3306"
db_user = "root"
db_pass = "Kawtar@123"
db_name = "marsa_maroc_db"

engine = create_engine(f"mysql+mysqlconnector://{db_user}:{quote_plus(db_pass)}@{db_host}:3306/{db_name}")

with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM conteneurs WHERE terminal = 'TC3' LIMIT 5"), conn)
    
    # Nettoyage des chaines si nécessaire
    for col in ['terminal', 'zone', 'allee', 'pile']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    res = json.loads(df.to_json(orient="records", date_format="iso"))
    print("SUCCESS:", type(res), type(res[0]))
    print(res[0])
