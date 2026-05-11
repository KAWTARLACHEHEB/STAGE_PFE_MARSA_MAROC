import sys
import os
sys.path.append('c:/Users/hp/Desktop/STAGE_PFE_MARSA_MAROC/app')
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

db_host = "127.0.0.1"
db_port = "3306" # Let me check what port main.py uses... wait, main.py uses 3307?
db_user = "root"
db_pass = "Kawtar@123" # I saw this password in server.js
db_name = "marsa_maroc_db"

# wait, in app/main.py:
# db_host = os.getenv("MYSQL_HOST", "127.0.0.1")
# db_port = os.getenv("MYSQL_PORT", "3307")
# db_user = os.getenv("MYSQL_USER", "root")
# db_pass = quote_plus(os.getenv("MYSQL_PASSWORD", "rootpassword"))

engine = create_engine(f"mysql+mysqlconnector://{db_user}:{quote_plus(db_pass)}@{db_host}:3306/{db_name}")

try:
    with engine.connect() as conn:
        print("Connected to DB")
        res = conn.execute(text("SELECT * FROM view_yard_congestion LIMIT 1"))
        print("Query success", res.fetchone())
except Exception as e:
    print("Error:", e)
