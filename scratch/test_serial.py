import sys
import os
sys.path.append('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/app')
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

db_host = "127.0.0.1"
db_port = "3306"
db_user = "root"
db_pass = "Kawtar@123"
db_name = "marsa_maroc_db"

engine = create_engine(f"mysql+mysqlconnector://{db_user}:{quote_plus(db_pass)}@{db_host}:3306/{db_name}")

with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM conteneurs WHERE terminal = 'TC3' LIMIT 5"), conn)
    print("Columns:", df.columns)
    print("Types:\n", df.dtypes)
    d = df.to_dict(orient='records')
    import json
    try:
        json.dumps(d)
        print("JSON Serialization SUCCESS")
    except Exception as e:
        print("JSON Serialization ERROR:", e)
